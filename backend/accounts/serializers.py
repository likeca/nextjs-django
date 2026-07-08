from dj_rest_auth.registration.serializers import RegisterSerializer as BaseRegisterSerializer
from dj_rest_auth.serializers import (
    PasswordResetConfirmSerializer as BasePasswordResetConfirmSerializer,
    PasswordResetSerializer as BasePasswordResetSerializer,
)
from django.conf import settings
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Permission, Role, RolePermission, User


class PermissionSerializer(serializers.ModelSerializer):
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = Permission
        fields = ("id", "name", "description", "resource", "action", "createdAt", "updatedAt")


class RoleSerializer(serializers.ModelSerializer):
    isSystem = serializers.BooleanField(source="is_system", required=False)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)
    permissions = serializers.SerializerMethodField()
    # Shape the former Prisma `rolePermissions: [{ permission }]` so the roles UI
    # (role.rolePermissions.map(rp => rp.permission)) keeps working unchanged.
    rolePermissions = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = (
            "id", "name", "description", "isSystem",
            "permissions", "rolePermissions", "createdAt", "updatedAt",
        )

    def _perms(self, obj):
        return [rp.permission for rp in obj.role_permissions.select_related("permission").all()]

    def get_permissions(self, obj):
        return PermissionSerializer(self._perms(obj), many=True).data

    def get_rolePermissions(self, obj):
        return [{"permission": PermissionSerializer(p).data} for p in self._perms(obj)]


class RoleSummarySerializer(serializers.ModelSerializer):
    """Lightweight role representation embedded in the user payload."""

    class Meta:
        model = Role
        fields = ("id", "name")


class UserSerializer(serializers.ModelSerializer):
    """Camel-cased user payload matching the former Prisma/better-auth shape."""

    emailVerified = serializers.BooleanField(source="email_verified", read_only=True)
    isAdmin = serializers.BooleanField(source="is_admin", read_only=True)
    roleId = serializers.PrimaryKeyRelatedField(source="role", read_only=True)
    role = RoleSummarySerializer(read_only=True)
    stripeCustomerId = serializers.CharField(source="stripe_customer_id", read_only=True)
    twoFactorEnabled = serializers.BooleanField(source="two_factor_enabled", read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "name",
            "email",
            "emailVerified",
            "image",
            "phone",
            "isAdmin",
            "roleId",
            "role",
            "stripeCustomerId",
            "twoFactorEnabled",
            "createdAt",
            "updatedAt",
        )
        # name / phone / image are writable so a user can PATCH /api/auth/user/
        # to update their own profile. Everything else is read-only.
        read_only_fields = ("id", "email")
        extra_kwargs = {
            "image": {"required": False, "allow_null": True, "allow_blank": True},
            "phone": {"required": False, "allow_null": True, "allow_blank": True},
        }


class AdminUserWriteSerializer(serializers.ModelSerializer):
    """Create/update users from the admin UI (replaces actions/users/*)."""

    isAdmin = serializers.BooleanField(source="is_admin", required=False)
    emailVerified = serializers.BooleanField(source="email_verified", required=False)
    roleId = serializers.PrimaryKeyRelatedField(
        source="role", queryset=Role.objects.all(), required=False, allow_null=True
    )
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = User
        fields = (
            "id", "name", "email", "phone", "image",
            "isAdmin", "emailVerified", "roleId", "password",
        )
        read_only_fields = ("id",)

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    def to_representation(self, instance):
        return UserSerializer(instance, context=self.context).data


class RoleWriteSerializer(serializers.ModelSerializer):
    """Create/update roles and (re)assign their permissions."""

    isSystem = serializers.BooleanField(source="is_system", required=False)
    permissionIds = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Permission.objects.all(),
        required=False,
        source="permissions_input",
    )

    class Meta:
        model = Role
        fields = ("id", "name", "description", "isSystem", "permissionIds")

    def _sync_permissions(self, role, permissions):
        RolePermission.objects.filter(role=role).delete()
        RolePermission.objects.bulk_create(
            [RolePermission(role=role, permission=p) for p in permissions]
        )

    def create(self, validated_data):
        permissions = validated_data.pop("permissions_input", [])
        role = Role.objects.create(**validated_data)
        self._sync_permissions(role, permissions)
        return role

    def update(self, instance, validated_data):
        permissions = validated_data.pop("permissions_input", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if permissions is not None:
            self._sync_permissions(instance, permissions)
        return instance

    def to_representation(self, instance):
        return RoleSerializer(instance, context=self.context).data


class PasswordResetSerializer(BasePasswordResetSerializer):
    """Send the reset email with a link to the Next.js /reset-password page
    (carrying uid + token), instead of Django's server-rendered confirm URL.

    Forces Django's PasswordResetForm (dj-rest-auth would otherwise use the
    allauth form, which ignores `email_template_name`).
    """

    @property
    def password_reset_form_class(self):
        from django.contrib.auth.forms import PasswordResetForm

        return PasswordResetForm

    def get_email_options(self):
        # token_generator must be Django's (not allauth's) so the token validates
        # in PasswordResetConfirmSerializer below.
        return {
            "email_template_name": "registration/password_reset_email.txt",
            "extra_email_context": {"frontend_url": settings.FRONTEND_URL},
            "token_generator": default_token_generator,
        }


class PasswordResetConfirmSerializer(BasePasswordResetConfirmSerializer):
    """Force Django's base64 uid + token decoder so it matches the (Django-form)
    reset request above. dj-rest-auth would otherwise use allauth's base36 decoder
    when allauth is installed, which can't decode our UUID-PK uid."""

    def validate(self, attrs):
        try:
            uid = force_str(urlsafe_base64_decode(attrs["uid"]))
            self.user = User._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise ValidationError({"uid": ["Invalid value"]})

        if not default_token_generator.check_token(self.user, attrs["token"]):
            raise ValidationError({"token": ["Invalid value"]})

        self.custom_validation(attrs)
        self.set_password_form = SetPasswordForm(user=self.user, data=attrs)
        if not self.set_password_form.is_valid():
            raise ValidationError(self.set_password_form.errors)
        return attrs


class RegisterSerializer(BaseRegisterSerializer):
    """Registration with a `name` field instead of username."""

    username = None
    name = serializers.CharField(max_length=255, required=True)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data["name"] = self.validated_data.get("name", "")
        return data

    def save(self, request):
        user = super().save(request)
        user.name = self.validated_data.get("name", "")
        user.save(update_fields=["name"])
        return user
