import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class Setting(models.Model):
    """Mirrors Prisma `Setting` — key/value app settings."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=200, unique=True)
    value = models.TextField()
    type = models.CharField(max_length=30, default="string")  # string|number|boolean|json
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "setting"
        indexes = [models.Index(fields=["key"])]

    def __str__(self):
        return self.key


class ApiKey(models.Model):
    """Mirrors Prisma `ApiKey`."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    key_hash = models.CharField(max_length=255, unique=True)
    key_prefix = models.CharField(max_length=20)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="api_keys"
    )
    last_used_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    revoked_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "api_key"
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["key_hash"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.key_prefix}…)"


class Organization(models.Model):
    """Mirrors Prisma `Organization`."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True, null=True)
    logo = models.URLField(max_length=500, blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_organizations",
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "organization"

    def __str__(self):
        return self.name


class OrganizationMember(models.Model):
    """Mirrors Prisma `OrganizationMember`."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="members"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organization_memberships",
    )
    role = models.CharField(max_length=50, default="member")
    joined_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "organization_member"
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "user"], name="uq_org_member"
            )
        ]


class OrganizationInvitation(models.Model):
    """Mirrors Prisma `OrganizationInvitation`."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="invitations"
    )
    email = models.EmailField()
    role = models.CharField(max_length=50, default="member")
    token = models.CharField(max_length=255, unique=True, default=uuid.uuid4)
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "organization_invitation"
        indexes = [
            models.Index(fields=["token"]),
            models.Index(fields=["email"]),
        ]


class ContactSubmission(models.Model):
    """Mirrors Prisma `ContactSubmission`."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    message = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    status = models.CharField(max_length=30, default="new")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "contact_submission"
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]


class Log(models.Model):
    """Mirrors Prisma `Log`."""

    id = models.BigAutoField(primary_key=True)
    message = models.TextField()
    level = models.CharField(max_length=20, default="info")
    metadata = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "log"
        indexes = [
            models.Index(fields=["level"]),
            models.Index(fields=["created_at"]),
        ]
