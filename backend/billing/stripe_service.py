"""Thin wrapper around the Stripe SDK + customer helper."""
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def get_stripe():
    return stripe


def create_or_retrieve_customer(user) -> str:
    """Return the user's Stripe customer id, creating one if needed."""
    if user.stripe_customer_id:
        return user.stripe_customer_id

    customer = stripe.Customer.create(
        email=user.email,
        name=user.name or None,
        metadata={"user_id": str(user.id)},
    )
    user.stripe_customer_id = customer.id
    user.save(update_fields=["stripe_customer_id"])
    return customer.id
