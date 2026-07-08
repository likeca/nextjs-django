from rest_framework import serializers

from .models import Payment, Plan, Subscription


class PlanSerializer(serializers.ModelSerializer):
    stripePriceId = serializers.CharField(source="stripe_price_id")
    stripeProductId = serializers.CharField(source="stripe_product_id")
    isPopular = serializers.BooleanField(source="is_popular")
    isActive = serializers.BooleanField(source="is_active")
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = Plan
        fields = (
            "id", "name", "description", "stripePriceId", "stripeProductId",
            "amount", "currency", "interval", "features", "isPopular", "isActive",
            "createdAt", "updatedAt",
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    userId = serializers.PrimaryKeyRelatedField(source="user", read_only=True)
    planId = serializers.PrimaryKeyRelatedField(source="plan", read_only=True)
    plan = PlanSerializer(read_only=True)
    stripeSubscriptionId = serializers.CharField(source="stripe_subscription_id", read_only=True)
    stripeCustomerId = serializers.CharField(source="stripe_customer_id", read_only=True)
    currentPeriodStart = serializers.DateTimeField(source="current_period_start", read_only=True)
    currentPeriodEnd = serializers.DateTimeField(source="current_period_end", read_only=True)
    cancelAtPeriodEnd = serializers.BooleanField(source="cancel_at_period_end", read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = Subscription
        fields = (
            "id", "userId", "planId", "plan", "stripeSubscriptionId", "stripeCustomerId",
            "status", "currentPeriodStart", "currentPeriodEnd", "cancelAtPeriodEnd",
            "createdAt", "updatedAt",
        )


class PaymentSerializer(serializers.ModelSerializer):
    stripePaymentId = serializers.CharField(source="stripe_payment_id", read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = Payment
        fields = ("id", "stripePaymentId", "amount", "currency", "status", "description", "createdAt")
