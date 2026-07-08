"""Stripe webhook → syncs Subscription / Payment rows. Replaces app/api/webhooks/stripe."""
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Payment, Plan, Subscription
from .stripe_service import get_stripe

logger = logging.getLogger("project")
User = get_user_model()


def _dt(ts):
    if not ts:
        return None
    return timezone.datetime.fromtimestamp(ts, tz=timezone.get_current_timezone())


def _resolve_user(stripe_customer_id, metadata):
    user_id = (metadata or {}).get("userId")
    if user_id:
        user = User.objects.filter(id=user_id).first()
        if user:
            return user
    return User.objects.filter(stripe_customer_id=stripe_customer_id).first()


def _upsert_subscription(sub_obj):
    """Create/update a Subscription row from a Stripe subscription object."""
    customer_id = sub_obj.get("customer")
    user = _resolve_user(customer_id, sub_obj.get("metadata"))
    if not user:
        logger.warning("Webhook: no user for customer %s", customer_id)
        return

    price_id = None
    items = sub_obj.get("items", {}).get("data", [])
    if items:
        price_id = items[0].get("price", {}).get("id")
    plan = Plan.objects.filter(stripe_price_id=price_id).first() if price_id else None
    if not plan:
        logger.warning("Webhook: no plan for price %s", price_id)
        return

    Subscription.objects.update_or_create(
        stripe_subscription_id=sub_obj["id"],
        defaults={
            "user": user,
            "plan": plan,
            "stripe_customer_id": customer_id,
            "status": sub_obj.get("status", "active"),
            "current_period_start": _dt(sub_obj.get("current_period_start")) or timezone.now(),
            "current_period_end": _dt(sub_obj.get("current_period_end")) or timezone.now(),
            "cancel_at_period_end": sub_obj.get("cancel_at_period_end", False),
        },
    )


@csrf_exempt
@require_POST
def stripe_webhook(request):
    stripe = get_stripe()
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        if secret:
            event = stripe.Webhook.construct_event(payload, sig_header, secret)
        else:
            # No secret configured (dev) — parse without verification.
            import json

            event = json.loads(payload)
    except ValueError:
        return HttpResponseBadRequest("Invalid payload")
    except Exception as exc:  # stripe.error.SignatureVerificationError, etc.
        logger.error("Webhook signature verification failed: %s", exc)
        return HttpResponseBadRequest("Invalid signature")

    event_type = event["type"]
    obj = event["data"]["object"]

    try:
        if event_type in (
            "customer.subscription.created",
            "customer.subscription.updated",
            "customer.subscription.deleted",
        ):
            _upsert_subscription(obj)

        elif event_type == "checkout.session.completed":
            sub_id = obj.get("subscription")
            if sub_id:
                _upsert_subscription(stripe.Subscription.retrieve(sub_id))

        elif event_type == "invoice.payment_succeeded":
            user = _resolve_user(obj.get("customer"), obj.get("metadata"))
            if user:
                Payment.objects.update_or_create(
                    stripe_payment_id=obj.get("id"),
                    defaults={
                        "user": user,
                        "amount": obj.get("amount_paid", 0),
                        "currency": obj.get("currency", "usd"),
                        "status": "succeeded",
                        "description": obj.get("description") or "Invoice payment",
                    },
                )
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("Webhook handling error for %s: %s", event_type, exc)
        return JsonResponse({"received": True, "handled": False})

    return JsonResponse({"received": True})
