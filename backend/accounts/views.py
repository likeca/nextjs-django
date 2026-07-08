import json
import secrets
from datetime import timedelta

import pyotp
from django.conf import settings as django_settings
from django.contrib.auth import authenticate, get_user_model
from django.core import signing
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import EmailChangeRequest, EmailOTP, Permission, Role, TwoFactor
from .permissions import HasResourcePermission, can_access_user, user_permission_summary

# Short-lived signed token used to bridge password-check → 2FA-verify at login.
PRE_AUTH_SALT = "accounts.pre-auth-2fa"
PRE_AUTH_MAX_AGE = 300  # seconds


def issue_jwt(user):
    """Return the dj-rest-auth-compatible {access, refresh, user} payload."""
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": UserSerializer(user).data,
    }


def verify_2fa_code(tf: TwoFactor, code: str) -> bool:
    """True if `code` is a valid TOTP or an unused backup code (which is consumed)."""
    code = (code or "").strip()
    if pyotp.TOTP(tf.secret).verify(code, valid_window=1):
        return True
    try:
        backup = json.loads(tf.backup_codes or "[]")
    except json.JSONDecodeError:
        backup = []
    if code in backup:
        backup.remove(code)
        tf.backup_codes = json.dumps(backup)
        tf.save(update_fields=["backup_codes"])
        return True
    return False


class LoginView(APIView):
    """Email+password login that gates 2FA-enabled users.

    Replaces the dj-rest-auth login endpoint. If the user has confirmed TOTP 2FA,
    no JWT is issued yet — a short-lived `preAuthToken` is returned and the client
    must complete /api/auth/2fa/login-verify/.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").strip().lower()
        password = request.data.get("password") or ""
        user = authenticate(request, username=email, password=password)
        if user is None or not user.is_active:
            return Response(
                {"detail": "Unable to log in with provided credentials."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tf = TwoFactor.objects.filter(user=user, confirmed=True).first()
        if user.two_factor_enabled and tf:
            pre_auth = signing.dumps({"user_id": str(user.id)}, salt=PRE_AUTH_SALT)
            return Response({"twoFactorRequired": True, "preAuthToken": pre_auth})

        return Response(issue_jwt(user))


class TwoFactorLoginVerifyView(APIView):
    """Exchange a preAuthToken + TOTP/backup code for real JWTs."""

    permission_classes = [AllowAny]

    def post(self, request):
        pre_auth = request.data.get("preAuthToken") or ""
        code = request.data.get("code") or ""
        try:
            data = signing.loads(pre_auth, salt=PRE_AUTH_SALT, max_age=PRE_AUTH_MAX_AGE)
        except signing.BadSignature:
            return Response({"error": "Invalid or expired session"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(id=data.get("user_id"), is_active=True).first()
        tf = TwoFactor.objects.filter(user=user, confirmed=True).first() if user else None
        if not user or not tf:
            return Response({"error": "Invalid or expired session"}, status=status.HTTP_400_BAD_REQUEST)
        if not verify_2fa_code(tf, code):
            return Response({"error": "Invalid authentication code"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(issue_jwt(user))
from .serializers import (
    AdminUserWriteSerializer,
    PermissionSerializer,
    RoleSerializer,
    RoleWriteSerializer,
    UserSerializer,
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """Admin user management — replaces actions/users/*."""

    queryset = User.objects.select_related("role").all().order_by("-created_at")
    permission_classes = [IsAuthenticated, HasResourcePermission]
    rbac_resource = "user"
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "email", "phone"]
    ordering_fields = ["created_at", "name", "email"]

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        if p.get("isAdmin") and p["isAdmin"] != "all":
            qs = qs.filter(is_admin=p["isAdmin"].lower() == "true")
        if p.get("role") and p["role"] != "all":
            qs = qs.filter(role_id=p["role"])
        ev = p.get("emailVerified")
        if ev and ev != "all":
            qs = qs.filter(email_verified=ev in ("verified", "true"))
        return qs

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return AdminUserWriteSerializer
        return UserSerializer

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Current authenticated user (no RBAC gate)."""
        return Response(UserSerializer(request.user, context={"request": request}).data)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def permissions(self, request):
        """Effective permission summary for the current user (drives client RBAC)."""
        return Response(user_permission_summary(request.user))

    def get_object(self):
        obj = super().get_object()
        # IDOR guard mirroring the former canAccessUser() used by get-user: a user
        # may always read themselves; reading *another* user needs Super Admin /
        # user.update_any. (update/destroy rely on the user.update/delete RBAC.)
        if self.action == "retrieve" and not can_access_user(self.request.user, str(obj.id)):
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("You cannot access this user.")
        return obj


class RoleViewSet(viewsets.ModelViewSet):
    """Replaces actions/roles/*."""

    queryset = Role.objects.prefetch_related("role_permissions__permission").all()
    permission_classes = [IsAuthenticated, HasResourcePermission]
    rbac_resource = "role"
    pagination_class = None  # roles are few; the UI expects the full list
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "description"]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return RoleWriteSerializer
        return RoleSerializer

    def perform_destroy(self, instance):
        from rest_framework.exceptions import ValidationError

        # System roles cannot be deleted (mirrors Prisma isSystem semantics).
        if instance.is_system:
            raise ValidationError("Cannot delete system roles.")
        # Block deletion while the role is still assigned to users.
        assigned = instance.users.count()
        if assigned > 0:
            raise ValidationError(
                f"Cannot delete role. It is currently assigned to {assigned} admin(s)."
            )
        instance.delete()


class DashboardStatsView(APIView):
    """Admin dashboard aggregates. Replaces app/(protected)/(admin)/dashboard/actions."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not (getattr(request.user, "is_admin", False) or request.user.is_superuser):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        # billing app disabled — revenue/subscription stats unavailable
        total_revenue = 0
        recent = User.objects.order_by("-created_at")[:5]
        return Response({
            "totalUsers": User.objects.count(),
            "activeSubscriptions": 0,
            "totalRevenue": total_revenue,
            "recentUsers": [
                {"id": str(u.id), "name": u.name, "email": u.email, "createdAt": u.created_at}
                for u in recent
            ],
        })


EMAIL_CHANGE_TOKEN_EXPIRY_HOURS = 24


class EmailChangeRequestView(APIView):
    """Request an email change: stores a token and emails the new address.
    Replaces app/api/user/email-change (POST)."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        new_email = (request.data.get("newEmail") or "").strip().lower()
        if not new_email:
            return Response({"error": "New email is required"}, status=status.HTTP_400_BAD_REQUEST)
        if new_email == request.user.email.lower():
            return Response(
                {"error": "New email must be different from current email"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if User.objects.filter(email__iexact=new_email).exists():
            return Response({"error": "This email is already in use"}, status=status.HTTP_400_BAD_REQUEST)

        EmailChangeRequest.objects.filter(user=request.user).delete()
        token = secrets.token_hex(32)
        EmailChangeRequest.objects.create(
            user=request.user,
            new_email=new_email,
            token=token,
            expires_at=timezone.now() + timedelta(hours=EMAIL_CHANGE_TOKEN_EXPIRY_HOURS),
        )

        verify_url = f"{django_settings.FRONTEND_URL}/verify-email-change?token={token}"
        try:
            send_mail(
                subject="Verify your new email address",
                message=f"Confirm your email change by visiting: {verify_url}",
                from_email=getattr(django_settings, "DEFAULT_FROM_EMAIL", None),
                recipient_list=[new_email],
                fail_silently=True,
            )
        except Exception:  # pragma: no cover - defensive
            pass

        return Response({
            "success": True,
            "message": "A verification email has been sent to your new email address.",
        })


class EmailChangeConfirmView(APIView):
    """Confirm an email change with the token. Replaces /verify-email-change flow."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)
        req = EmailChangeRequest.objects.filter(token=token).first()
        if not req or req.expires_at < timezone.now():
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email__iexact=req.new_email).exclude(id=req.user_id).exists():
            return Response({"error": "This email is already in use"}, status=status.HTTP_400_BAD_REQUEST)

        user = req.user
        new_email = req.new_email
        user.email = new_email
        user.email_verified = True
        user.save(update_fields=["email", "email_verified"])
        req.delete()
        return Response({"success": True, "message": "Email updated successfully", "newEmail": new_email})


OTP_EXPIRY_MINUTES = 10
TOTP_ISSUER = "SaaS App"


class EmailOTPSendView(APIView):
    """Send a one-time email verification code. Replaces better-auth emailOtp.sendVerificationOtp."""

    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").strip().lower()
        purpose = request.data.get("type") or "email-verification"
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        code = f"{secrets.randbelow(1000000):06d}"
        EmailOTP.objects.filter(email=email, purpose=purpose).delete()
        EmailOTP.objects.create(
            email=email,
            code=code,
            purpose=purpose,
            expires_at=timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES),
        )
        try:
            send_mail(
                subject="Your verification code",
                message=f"Your verification code is {code}. It expires in {OTP_EXPIRY_MINUTES} minutes.",
                from_email=getattr(django_settings, "DEFAULT_FROM_EMAIL", None),
                recipient_list=[email],
                fail_silently=True,
            )
        except Exception:  # pragma: no cover - defensive
            pass
        return Response({"success": True})


class EmailOTPVerifyView(APIView):
    """Verify an email OTP and mark the user's email as verified."""

    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").strip().lower()
        otp = (request.data.get("otp") or "").strip()
        purpose = request.data.get("type") or "email-verification"
        if not email or not otp:
            return Response({"error": "Email and code are required"}, status=status.HTTP_400_BAD_REQUEST)

        rec = EmailOTP.objects.filter(email=email, purpose=purpose, code=otp).first()
        if not rec or rec.expires_at < timezone.now():
            return Response({"error": "Invalid or expired code"}, status=status.HTTP_400_BAD_REQUEST)

        EmailOTP.objects.filter(email=email, purpose=purpose).delete()
        user = User.objects.filter(email__iexact=email).first()
        if user and not user.email_verified:
            user.email_verified = True
            user.save(update_fields=["email_verified"])
        return Response({"success": True})


class TwoFactorEnableView(APIView):
    """Begin TOTP enrollment: verify password, return otpauth URI + backup codes.
    Replaces better-auth twoFactor.enable. Not active until verified."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        password = request.data.get("password") or ""
        if not request.user.check_password(password):
            return Response({"error": "Incorrect password"}, status=status.HTTP_400_BAD_REQUEST)

        secret = pyotp.random_base32()
        backup_codes = [secrets.token_hex(4) for _ in range(10)]
        TwoFactor.objects.update_or_create(
            user=request.user,
            defaults={"secret": secret, "backup_codes": json.dumps(backup_codes), "confirmed": False},
        )
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=request.user.email, issuer_name=TOTP_ISSUER
        )
        return Response({"totpURI": totp_uri, "backupCodes": backup_codes})


class TwoFactorVerifyView(APIView):
    """Verify a TOTP code; activates 2FA on first success. Replaces twoFactor.verifyTotp."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = (request.data.get("code") or "").strip()
        tf = TwoFactor.objects.filter(user=request.user).first()
        if not tf:
            return Response({"error": "Two-factor is not set up"}, status=status.HTTP_400_BAD_REQUEST)
        if not pyotp.TOTP(tf.secret).verify(code, valid_window=1):
            return Response({"error": "Invalid authentication code"}, status=status.HTTP_400_BAD_REQUEST)
        if not tf.confirmed:
            tf.confirmed = True
            tf.save(update_fields=["confirmed"])
            request.user.two_factor_enabled = True
            request.user.save(update_fields=["two_factor_enabled"])
        return Response({"success": True})


class TwoFactorDisableView(APIView):
    """Disable 2FA after password confirmation. Replaces twoFactor.disable."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        password = request.data.get("password") or ""
        if not request.user.check_password(password):
            return Response({"error": "Incorrect password"}, status=status.HTTP_400_BAD_REQUEST)
        TwoFactor.objects.filter(user=request.user).delete()
        request.user.two_factor_enabled = False
        request.user.save(update_fields=["two_factor_enabled"])
        return Response({"success": True})


class PermissionViewSet(viewsets.ModelViewSet):
    """Replaces actions/permissions/*."""

    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, HasResourcePermission]
    rbac_resource = "permission"
    pagination_class = None  # the role editor needs the full permission list
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "resource", "action", "description"]

    def perform_destroy(self, instance):
        from rest_framework.exceptions import ValidationError

        assigned = instance.role_permissions.count()
        if assigned > 0:
            raise ValidationError(
                f"Cannot delete permission. It is currently assigned to {assigned} role(s)."
            )
        instance.delete()
