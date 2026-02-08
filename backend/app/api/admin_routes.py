import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.core.auth import require_admin, CurrentUser
from app.core.supabase_client import get_supabase

router = APIRouter(prefix="/admin", tags=["admin"])


# ── User Management ──────────────────────────────────────────


@router.get("/users")
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[str] = None,
    tier: Optional[str] = None,
    admin: CurrentUser = Depends(require_admin),
):
    def _query():
        sb = get_supabase()
        q = sb.table("profiles").select("*", count="exact")
        if search:
            q = q.or_(f"email.ilike.%{search}%,full_name.ilike.%{search}%")
        if role:
            q = q.eq("role", role)
        if tier:
            q = q.eq("tier", tier)
        offset = (page - 1) * per_page
        return q.order("created_at", desc=True).range(offset, offset + per_page - 1).execute()

    result = await asyncio.to_thread(_query)
    return {
        "users": result.data,
        "total": result.count,
        "page": page,
        "per_page": per_page,
    }


@router.get("/users/{user_id}")
async def get_user(user_id: str, admin: CurrentUser = Depends(require_admin)):
    def _fetch_profile():
        sb = get_supabase()
        return sb.table("profiles").select("*").eq("id", user_id).single().execute()

    profile = await asyncio.to_thread(_fetch_profile)
    if not profile.data:
        raise HTTPException(status_code=404, detail="User not found")

    def _fetch_usage():
        sb = get_supabase()
        return (
            sb.table("usage_logs")
            .select("*", count="exact")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(10)
            .execute()
        )

    def _fetch_subscription():
        sb = get_supabase()
        return (
            sb.table("subscriptions")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )

    usage, subscription = await asyncio.gather(
        asyncio.to_thread(_fetch_usage),
        asyncio.to_thread(_fetch_subscription),
    )

    return {
        "profile": profile.data,
        "total_generations": usage.count,
        "recent_usage": usage.data or [],
        "subscription": subscription.data[0] if subscription.data else None,
    }


class UserUpdate(BaseModel):
    role: Optional[str] = None
    tier: Optional[str] = None
    is_active: Optional[bool] = None
    full_name: Optional[str] = None


@router.patch("/users/{user_id}")
async def update_user(
    user_id: str,
    body: UserUpdate,
    admin: CurrentUser = Depends(require_admin),
):
    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    if "role" in updates and updates["role"] not in ("user", "admin"):
        raise HTTPException(status_code=400, detail="Invalid role")
    if "tier" in updates and updates["tier"] not in ("free", "pro", "enterprise"):
        raise HTTPException(status_code=400, detail="Invalid tier")

    def _update():
        sb = get_supabase()
        return sb.table("profiles").update(updates).eq("id", user_id).execute()

    result = await asyncio.to_thread(_update)
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")
    return {"updated": result.data}


# ── Analytics ────────────────────────────────────────────────


@router.get("/analytics/overview")
async def analytics_overview(admin: CurrentUser = Depends(require_admin)):
    def _count(table: str, **filters):
        sb = get_supabase()
        q = sb.table(table).select("id", count="exact")
        for k, v in filters.items():
            q = q.eq(k, v)
        return q.execute().count

    total, active, pro, enterprise, generations = await asyncio.gather(
        asyncio.to_thread(_count, "profiles"),
        asyncio.to_thread(_count, "profiles", is_active=True),
        asyncio.to_thread(_count, "profiles", tier="pro"),
        asyncio.to_thread(_count, "profiles", tier="enterprise"),
        asyncio.to_thread(_count, "usage_logs"),
    )

    return {
        "total_users": total,
        "active_users": active,
        "pro_users": pro,
        "enterprise_users": enterprise,
        "total_generations": generations,
    }


@router.get("/analytics/usage")
async def analytics_usage(
    days: int = Query(30, ge=1, le=365),
    admin: CurrentUser = Depends(require_admin),
):
    """Return generation data for the last N days."""
    def _query():
        sb = get_supabase()
        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        return (
            sb.table("usage_logs")
            .select("created_at, mode, tool")
            .gte("created_at", since)
            .order("created_at", desc=False)
            .execute()
        )

    result = await asyncio.to_thread(_query)
    return {"usage": result.data, "days": days}


@router.get("/analytics/tiers")
async def analytics_tiers(admin: CurrentUser = Depends(require_admin)):
    """Breakdown of users by tier."""
    def _count_tier(tier_name: str):
        sb = get_supabase()
        return (
            sb.table("profiles")
            .select("id", count="exact")
            .eq("tier", tier_name)
            .execute()
            .count
        )

    free, pro, enterprise = await asyncio.gather(
        asyncio.to_thread(_count_tier, "free"),
        asyncio.to_thread(_count_tier, "pro"),
        asyncio.to_thread(_count_tier, "enterprise"),
    )

    return {
        "tiers": [
            {"tier": "free", "count": free},
            {"tier": "pro", "count": pro},
            {"tier": "enterprise", "count": enterprise},
        ]
    }
