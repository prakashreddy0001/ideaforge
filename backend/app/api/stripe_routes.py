import asyncio
import logging

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request

from app.core.auth import get_current_user, CurrentUser
from app.core.config import settings
from app.core.supabase_client import get_supabase
from app.services.stripe_service import (
    create_checkout_session,
    create_portal_session,
    handle_webhook_event,
    get_tier_from_price,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stripe", tags=["stripe"])


@router.post("/checkout")
async def checkout(tier: str, user: CurrentUser = Depends(get_current_user)):
    """Create a Stripe checkout session for upgrading."""
    price_map = {
        "pro": settings.stripe_pro_price_id,
        "enterprise": settings.stripe_enterprise_price_id,
    }
    price_id = price_map.get(tier)
    if not price_id:
        raise HTTPException(status_code=400, detail="Invalid tier")

    try:
        url = await asyncio.to_thread(
            create_checkout_session,
            user_id=user.id,
            email=user.email,
            price_id=price_id,
            success_url=f"{settings.frontend_url}/dashboard?payment=success",
            cancel_url=f"{settings.frontend_url}/pricing?payment=canceled",
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return {"checkout_url": url}


@router.post("/portal")
async def portal(user: CurrentUser = Depends(get_current_user)):
    """Create a Stripe billing portal session."""
    def _get_customer():
        sb = get_supabase()
        profile = (
            sb.table("profiles")
            .select("stripe_customer_id")
            .eq("id", user.id)
            .single()
            .execute()
        )
        return profile.data.get("stripe_customer_id") if profile.data else None

    customer_id = await asyncio.to_thread(_get_customer)
    if not customer_id:
        raise HTTPException(status_code=400, detail="No billing account found")

    try:
        url = await asyncio.to_thread(
            create_portal_session, customer_id, f"{settings.frontend_url}/dashboard"
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return {"portal_url": url}


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events. Verified by signature, no auth."""
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")

    try:
        event = handle_webhook_event(payload, sig)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.warning("Webhook signature verification failed: %s", e)
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    sb = get_supabase()
    event_type = event["type"]
    data = event["data"]["object"]

    try:
        if event_type == "checkout.session.completed":
            metadata = data.get("metadata") or {}
            user_id = metadata.get("supabase_user_id")
            subscription_id = data.get("subscription")
            if user_id and subscription_id:
                sub = stripe.Subscription.retrieve(subscription_id)
                items = sub.get("items", {}).get("data", [])
                if not items:
                    logger.warning("No items in subscription %s", subscription_id)
                    return {"status": "ok"}
                price_id = items[0]["price"]["id"]
                tier = get_tier_from_price(price_id)

                sb.table("subscriptions").upsert(
                    {
                        "user_id": user_id,
                        "stripe_subscription_id": subscription_id,
                        "stripe_price_id": price_id,
                        "tier": tier,
                        "status": "active",
                    },
                    on_conflict="stripe_subscription_id",
                ).execute()

                sb.table("profiles").update({"tier": tier}).eq("id", user_id).execute()

        elif event_type == "customer.subscription.updated":
            sub_id = data.get("id")
            items = data.get("items", {}).get("data", [])
            if not items or not sub_id:
                return {"status": "ok"}
            price_id = items[0]["price"]["id"]
            tier = get_tier_from_price(price_id)
            sub_status = data.get("status", "active")

            sb.table("subscriptions").update(
                {
                    "tier": tier,
                    "status": sub_status,
                    "stripe_price_id": price_id,
                    "cancel_at_period_end": data.get("cancel_at_period_end", False),
                }
            ).eq("stripe_subscription_id", sub_id).execute()

            sub_record = (
                sb.table("subscriptions")
                .select("user_id")
                .eq("stripe_subscription_id", sub_id)
                .single()
                .execute()
            )
            if sub_record.data:
                effective_tier = tier if sub_status == "active" else "free"
                sb.table("profiles").update({"tier": effective_tier}).eq(
                    "id", sub_record.data["user_id"]
                ).execute()

        elif event_type == "customer.subscription.deleted":
            sub_id = data.get("id")
            if not sub_id:
                return {"status": "ok"}
            sb.table("subscriptions").update({"status": "canceled"}).eq(
                "stripe_subscription_id", sub_id
            ).execute()
            sub_record = (
                sb.table("subscriptions")
                .select("user_id")
                .eq("stripe_subscription_id", sub_id)
                .single()
                .execute()
            )
            if sub_record.data:
                sb.table("profiles").update({"tier": "free"}).eq(
                    "id", sub_record.data["user_id"]
                ).execute()

        elif event_type == "invoice.payment_failed":
            sub_id = data.get("subscription")
            if sub_id:
                sb.table("subscriptions").update({"status": "past_due"}).eq(
                    "stripe_subscription_id", sub_id
                ).execute()

    except Exception:
        logger.exception("Error processing webhook event %s", event_type)
        raise HTTPException(status_code=500, detail="Webhook processing failed")

    return {"status": "ok"}
