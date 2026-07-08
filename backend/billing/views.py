import logging

from django.conf import settings
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Payment, Plan, Subscription
from .serializers import PaymentSerializer, PlanSerializer, SubscriptionSerializer
from .stripe_service import create_or_retrieve_customer, get_stripe

logger = logging.getLogger("project")


class PlanViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Public list of active plans — replaces actions/payments/get-plans."""

    serializer_class = PlanSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        return Plan.objects.filter(is_active=True).order_by("amount")


class SubscriptionViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Current user's subscriptions — replaces actions/payments/get-*-subscription(s)."""

    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return (
            Subscription.objects.select_related("plan")
            .filter(user=self.request.user)
            .order_by("-created_at")
        )

    @action(detail=False, methods=["get"])
    def current(self, request):
        """The user's active subscription, or null."""
        sub = self.get_queryset().filter(status__in=["active", "trialing"]).first()
        data = self.get_serializer(sub).data if sub else None
        return Response({"success": True, "subscription": data})


class PaymentViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).order_by("-created_at")


# ─── Stripe actions (replace actions/payments/*) ──────────────────────────────
class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan_id = request.data.get("planId") or request.data.get("plan_id")
        if not plan_id:
            return Response({"error": "Invalid plan"}, status=status.HTTP_400_BAD_REQUEST)

        plan = Plan.objects.filter(id=plan_id, is_active=True).first()
        if not plan:
            return Response({"error": "Plan not available"}, status=status.HTTP_400_BAD_REQUEST)

        stripe = get_stripe()
        try:
            customer_id = create_or_retrieve_customer(request.user)
            checkout = stripe.checkout.Session.create(
                customer=customer_id,
                mode="subscription",
                payment_method_types=["card"],
                line_items=[{"price": plan.stripe_price_id, "quantity": 1}],
                success_url=f"{settings.FRONTEND_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.FRONTEND_URL}/payment/cancel?from=checkout",
                metadata={"userId": str(request.user.id), "planId": str(plan.id)},
            )
            return Response({"url": checkout.url})
        except Exception as exc:
            logger.error("Stripe checkout failed: %s", exc)
            return Response({"error": "Unable to process request"}, status=status.HTTP_502_BAD_GATEWAY)


class CreateBillingPortalSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.stripe_customer_id:
            return Response({"error": "No billing information available"}, status=status.HTTP_400_BAD_REQUEST)
        stripe = get_stripe()
        try:
            portal = stripe.billing_portal.Session.create(
                customer=request.user.stripe_customer_id,
                return_url=f"{settings.FRONTEND_URL}/billing",
            )
            return Response({"url": portal.url})
        except Exception as exc:
            logger.error("Stripe portal failed: %s", exc)
            return Response({"error": "Unable to access billing portal"}, status=status.HTTP_502_BAD_GATEWAY)


class CancelSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        sub = self._get_owned(request)
        if sub is None:
            return Response({"error": "Subscription not found"}, status=status.HTTP_404_NOT_FOUND)
        stripe = get_stripe()
        try:
            stripe.Subscription.modify(sub.stripe_subscription_id, cancel_at_period_end=True)
            sub.cancel_at_period_end = True
            sub.save(update_fields=["cancel_at_period_end"])
            return Response({"success": "Subscription will be canceled at the end of the period"})
        except Exception as exc:
            logger.error("Stripe cancel failed: %s", exc)
            return Response({"error": "Unable to cancel subscription"}, status=status.HTTP_502_BAD_GATEWAY)

    def _get_owned(self, request):
        sub_id = request.data.get("subscriptionId") or request.data.get("subscription_id")
        return Subscription.objects.filter(id=sub_id, user=request.user).first() if sub_id else None


class ResumeSubscriptionView(CancelSubscriptionView):
    def post(self, request):
        sub = self._get_owned(request)
        if sub is None:
            return Response({"error": "Subscription not found"}, status=status.HTTP_404_NOT_FOUND)
        stripe = get_stripe()
        try:
            stripe.Subscription.modify(sub.stripe_subscription_id, cancel_at_period_end=False)
            sub.cancel_at_period_end = False
            sub.save(update_fields=["cancel_at_period_end"])
            return Response({"success": "Subscription resumed"})
        except Exception as exc:
            logger.error("Stripe resume failed: %s", exc)
            return Response({"error": "Unable to resume subscription"}, status=status.HTTP_502_BAD_GATEWAY)


class VerifyCheckoutSessionView(APIView):
    """Verify a completed checkout and upsert the subscription/payment as a
    fallback to the webhook. Replaces actions/payments/verify-checkout-session."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        session_id = request.query_params.get("session_id")
        if not session_id:
            return Response({"error": "session_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        from .webhooks import _upsert_subscription

        stripe = get_stripe()
        try:
            checkout = stripe.checkout.Session.retrieve(session_id)
            if checkout.payment_status != "paid":
                return Response({"error": "Payment not completed"}, status=status.HTTP_400_BAD_REQUEST)

            sub_id = checkout.get("subscription")
            if sub_id:
                if Subscription.objects.filter(stripe_subscription_id=sub_id).exists():
                    return Response({"success": True, "alreadyExists": True})
                _upsert_subscription(stripe.Subscription.retrieve(sub_id))

            payment_intent = checkout.get("payment_intent")
            if payment_intent:
                Payment.objects.update_or_create(
                    stripe_payment_id=payment_intent,
                    defaults={
                        "user": request.user,
                        "amount": checkout.get("amount_total") or 0,
                        "currency": checkout.get("currency") or "usd",
                        "status": "succeeded",
                        "description": "Subscription payment",
                    },
                )
            return Response({"success": True})
        except Exception as exc:
            logger.error("Stripe verify failed: %s", exc)
            return Response({"error": "Failed to verify checkout session"}, status=status.HTTP_502_BAD_GATEWAY)
