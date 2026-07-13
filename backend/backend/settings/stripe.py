"""Stripe + frontend URL settings for the billing app."""
from .env_vars import env

STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY", default="")
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET", default="")

# Where the Next.js frontend lives — used for Stripe success/cancel/return URLs.
FRONTEND_URL = env("FRONTEND_URL", default="http://localhost:3000")
