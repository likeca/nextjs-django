import hashlib
import logging
import secrets

from django.conf import settings as django_settings
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import HasResourcePermission

from django.db import models as dj_models
from django.utils.text import slugify

from .models import (
    ApiKey,
    ContactSubmission,
    Organization,
    OrganizationMember,
    Setting,
)
from .serializers import (
    ApiKeySerializer,
    ContactSubmissionSerializer,
    OrganizationMemberSerializer,
    OrganizationSerializer,
    SettingSerializer,
)

logger = logging.getLogger("project")

# Mirrors PUBLIC_SETTING_KEYS in the former Next.js actions/settings/get-public-settings.ts
PUBLIC_SETTING_KEYS = [
    "companyName", "email", "phone", "address", "city", "state", "zipCode",
    "country", "businessHours", "googleMapsUrl", "whatsappNumber", "footerText",
    "meta", "facebook", "twitter", "instagram", "linkedin", "youtube", "tiktok",
]


class SettingViewSet(viewsets.ModelViewSet):
    """Replaces actions/settings/*."""

    queryset = Setting.objects.all().order_by("key")
    serializer_class = SettingSerializer
    permission_classes = [IsAuthenticated, HasResourcePermission]
    rbac_resource = "settings"
    pagination_class = None  # settings are few; the UI loads them all at once
    lookup_field = "key"
    lookup_value_regex = "[^/]+"

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def public(self, request):
        """Public settings map with defaults (no auth)."""
        data = {key: "" for key in PUBLIC_SETTING_KEYS}
        for s in Setting.objects.filter(key__in=PUBLIC_SETTING_KEYS):
            data[s.key] = s.value or ""
        return Response({"success": True, "data": data})

    @action(detail=False, methods=["put", "patch"])
    def bulk(self, request):
        """Upsert many settings at once: {"settings": {"key": "value", ...}}."""
        incoming = request.data.get("settings", request.data)
        if not isinstance(incoming, dict):
            return Response(
                {"error": "Expected a settings object."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        for key, value in incoming.items():
            Setting.objects.update_or_create(key=key, defaults={"value": str(value)})
        return self.public(request)


class ContactSubmissionViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Public create (contact form) + permissioned management. Replaces actions/contact/*."""

    queryset = ContactSubmission.objects.all().order_by("-created_at")
    serializer_class = ContactSubmissionSerializer
    rbac_resource = "contact"

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return [IsAuthenticated(), HasResourcePermission()]

    def _client_ip(self, request):
        fwd = request.META.get("HTTP_X_FORWARDED_FOR")
        if fwd:
            return fwd.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")

    def perform_create(self, serializer):
        submission = serializer.save(ip_address=self._client_ip(self.request))
        self._notify_admin(submission)

    def _notify_admin(self, submission):
        """Best-effort email notification (failure must not break submission)."""
        admin_setting = Setting.objects.filter(key="email").first()
        to_email = admin_setting.value if admin_setting else getattr(
            django_settings, "DEFAULT_FROM_EMAIL", None
        )
        if not to_email:
            return
        try:
            send_mail(
                subject=f"New contact inquiry from {submission.full_name}",
                message=(
                    f"From: {submission.full_name} <{submission.email}>\n"
                    f"Phone: {submission.phone_number or '-'}\n\n"
                    f"{submission.message}"
                ),
                from_email=getattr(django_settings, "DEFAULT_FROM_EMAIL", None),
                recipient_list=[to_email],
                fail_silently=True,
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Failed to send contact notification: %s", exc)


class ApiKeyViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Per-user API keys. Replaces app/api/api-keys. Raw key returned once on create."""

    serializer_class = ApiKeySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return ApiKey.objects.filter(user=self.request.user, revoked_at__isnull=True).order_by(
            "-created_at"
        )

    def create(self, request, *args, **kwargs):
        name = (request.data.get("name") or "").strip()
        if not name:
            return Response({"error": "Key name is required"}, status=status.HTTP_400_BAD_REQUEST)
        raw_key = f"sk_live_{secrets.token_hex(24)}"
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        key_prefix = raw_key[:12]
        api_key = ApiKey.objects.create(
            name=name, key_hash=key_hash, key_prefix=key_prefix, user=request.user
        )
        # The raw key is shown only once, never stored in plaintext.
        return Response(
            {
                "id": str(api_key.id),
                "name": api_key.name,
                "key": raw_key,
                "keyPrefix": key_prefix,
                "createdAt": api_key.created_at,
            },
            status=status.HTTP_201_CREATED,
        )

    def perform_destroy(self, instance):
        # Soft-revoke instead of hard delete.
        instance.revoked_at = timezone.now()
        instance.save(update_fields=["revoked_at"])


class OrganizationViewSet(viewsets.ModelViewSet):
    """Organizations the current user owns or belongs to. Replaces app/api/organizations."""

    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        return (
            Organization.objects.filter(dj_models.Q(owner=user) | dj_models.Q(members__user=user))
            .distinct()
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        name = serializer.validated_data.get("name", "")
        base_slug = slugify(serializer.validated_data.get("slug") or name) or "org"
        slug = base_slug
        if Organization.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{secrets.token_hex(4)}"
        org = serializer.save(owner=self.request.user, slug=slug)
        # The owner is also an (owner-role) member.
        OrganizationMember.objects.get_or_create(
            organization=org, user=self.request.user, defaults={"role": "owner"}
        )

    @action(detail=True, methods=["get"])
    def members(self, request, pk=None):
        org = self.get_object()
        qs = org.members.select_related("user").order_by("joined_at")
        return Response({"members": OrganizationMemberSerializer(qs, many=True).data})

    @action(detail=True, methods=["post"], url_path="remove-member")
    def remove_member(self, request, pk=None):
        org = self.get_object()
        user_id = request.data.get("userId")
        if str(user_id) == str(request.user.id):
            return Response({"error": "Cannot remove yourself"}, status=status.HTTP_400_BAD_REQUEST)
        # Only owner/admin may remove members.
        actor = org.members.filter(user=request.user).first()
        if not (org.owner_id == request.user.id or (actor and actor.role in ("owner", "admin"))):
            return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        OrganizationMember.objects.filter(organization=org, user_id=user_id).delete()
        return Response({"success": True})
