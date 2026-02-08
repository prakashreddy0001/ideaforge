import stripe

from app.core.config import settings

stripe.api_key = settings.stripe_secret_key

TIER_PRICE_MAP = {
    settings.stripe_pro_price_id: "pro",
    settings.stripe_enterprise_price_id: "enterprise",
}


def create_checkout_session(
    user_id: str,
    email: str,
    price_id: str,
    success_url: str,
    cancel_url: str,
) -> str:
    """Create a Stripe Checkout session and return the URL."""
    from app.core.supabase_client import get_supabase

    sb = get_supabase()

    # Get or create Stripe customer
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
    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )
    return session.url


def handle_webhook_event(payload: bytes, sig_header: str):
    """Verify and parse a Stripe webhook event."""
    event = stripe.Webhook.construct_event(
        payload, sig_header, settings.stripe_webhook_secret
    )
    return event
