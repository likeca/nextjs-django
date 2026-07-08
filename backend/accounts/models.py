import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from .managers import UserManager


class Role(models.Model):
    """Mirrors Prisma `Role`."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    # System roles cannot be deleted
    is_system = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "role"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Permission(models.Model):
    """Mirrors Prisma `Permission` (app-level RBAC, distinct from auth.Permission)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True, null=True)
    resource = models.CharField(max_length=100)  # e.g. "user", "blog", "settings"
    action = models.CharField(max_length=50)      # e.g. "create", "read", "update", "delete"
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "permission"
        ordering = ["resource", "action"]
        constraints = [
            models.UniqueConstraint(
                fields=["resource", "action"], name="uq_permission_resource_action"
            )
        ]

    def __str__(self):
        return self.name


class RolePermission(models.Model):
    """Join table mirroring Prisma `RolePermission`."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(
        Role, on_delete=models.CASCADE, related_name="role_permissions"
    )
    permission = models.ForeignKey(
        Permission, on_delete=models.CASCADE, related_name="role_permissions"
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "role_permission"
        constraints = [
            models.UniqueConstraint(
                fields=["role", "permission"], name="uq_role_permission"
            )
        ]
        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["permission"]),
        ]

    def __str__(self):
        return f"{self.role} → {self.permission}"


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user mirroring Prisma `User` (email-based login)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False)
    image = models.URLField(max_length=500, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)

    # `isAdmin` in Prisma — app-level admin flag (separate from is_staff/is_superuser)
    is_admin = models.BooleanField(default=False)
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )

    stripe_customer_id = models.CharField(
        max_length=255, unique=True, null=True, blank=True
    )
    two_factor_enabled = models.BooleanField(default=False)

    # Django auth flags
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        db_table = "user"
        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["is_admin"]),
        ]

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name or self.email.split("@")[0]


class EmailChangeRequest(models.Model):
    """Mirrors Prisma `EmailChangeRequest`."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="email_change_requests"
    )
    new_email = models.EmailField()
    token = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "email_change_request"
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["token"]),
        ]


class TwoFactor(models.Model):
    """Mirrors Prisma `TwoFactor`."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="two_factor"
    )
    secret = models.CharField(max_length=255)
    backup_codes = models.TextField()
    # Pending until the user verifies their first TOTP code.
    confirmed = models.BooleanField(default=False)

    class Meta:
        db_table = "two_factor"


class EmailOTP(models.Model):
    """One-time codes for email verification (replaces better-auth's emailOTP plugin)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(db_index=True)
    code = models.CharField(max_length=10)
    purpose = models.CharField(max_length=30, default="email-verification")
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "email_otp"
        indexes = [models.Index(fields=["email", "purpose"])]
