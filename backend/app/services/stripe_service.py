import logging

import stripe

from app.core.config import settings

logger = logging.getLogger(__name__)

_stripe_ready = False


def _ensure_stripe():
    """Lazy-init Stripe — only runs when a Stripe endpoint is actually called."""
    global _stripe_ready
    if _stripe_ready:
        return
    if not settings.stripe_secret_key:
        raise RuntimeError("Stripe is not configured (STRIPE_SECRET_KEY missing)")
    stripe.api_key = settings.stripe_secret_key
    _stripe_ready = True


def get_tier_from_price(price_id: str) -> str:
    """Map a Stripe price ID to a tier name."""
    price_map = {
        settings.stripe_pro_price_id: "pro",
        settings.stripe_enterprise_price_id: "enterprise",
    }
    return price_map.get(price_id, "pro")


# Backward-compatible constant — built lazily on first use
TIER_PRICE_MAP: dict = {}


def create_checkout_session(
    user_id: str,
    email: str,
    price_id: str,
    success_url: str,
    cancel_url: str,
) -> str:
    """Create a Stripe Checkout session and return the URL."""
    _ensure_stripe()
    from app.core.supabase_client import get_supabase

    sb = get_supabase()

    profile = (
        sb.table("profiles")
        .select("stripe_customer_id")
        .eq("id", user_id)
        .single()
        .execute()
    )
    customer_id = profile.data.get("stripe_customer_id") if profile.data else None

    if not customer_id:
        customer = stripe.Customer.create(
            email=email,
            metadata={"supabase_user_id": user_id},
        )
        customer_id = customer.id
        sb.table("profiles").update(
            {"stripe_customer_id": customer_id}
        ).eq("id", user_id).execute()

    session = stripe.checkout.Session.create(
        customer=customer_id,
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"supabase_user_id": user_id},
    )
    return session.url


def create_portal_session(customer_id: str, return_url: str) -> str:
    """Create a Stripe billing portal session."""
    _ensure_stripe()
    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )
    return session.url


def handle_webhook_event(payload: bytes, sig_header: str):
    """Verify and parse a Stripe webhook event."""
    _ensure_stripe()
    if not settings.stripe_webhook_secret:
        raise RuntimeError("Stripe webhook secret not configured")
    event = stripe.Webhook.construct_event(
        payload, sig_header, settings.stripe_webhook_secret
    )
    return event
