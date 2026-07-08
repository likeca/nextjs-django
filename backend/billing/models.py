import uuid

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone


class Plan(models.Model):
    """Mirrors Prisma `Plan`."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    stripe_price_id = models.CharField(max_length=255, unique=True)
    stripe_product_id = models.CharField(max_length=255)
    amount = models.IntegerField()  # in the smallest currency unit (e.g. cents)
    currency = models.CharField(max_length=10, default="usd")
    interval = models.CharField(max_length=20)  # "month" | "year"
    features = ArrayField(models.CharField(max_length=255), default=list, blank=True)
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "plan"
        indexes = [
            models.Index(fields=["interval"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name


class Subscription(models.Model):
    """Mirrors Prisma `Subscription`."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions"
    )
    plan = models.ForeignKey(
        Plan, on_delete=models.PROTECT, related_name="subscriptions"
    )
    stripe_subscription_id = models.CharField(max_length=255, unique=True)
    stripe_customer_id = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    cancel_at_period_end = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "subscription"
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["plan"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.user} · {self.plan} ({self.status})"


class Payment(models.Model):
    """Mirrors Prisma `Payment`."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments"
    )
    stripe_payment_id = models.CharField(max_length=255, unique=True)
    amount = models.IntegerField()
    currency = models.CharField(max_length=10, default="usd")
    status = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payment"
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["status"]),
        ]
