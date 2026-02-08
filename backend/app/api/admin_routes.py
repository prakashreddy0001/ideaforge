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
    sb = get_supabase()
    query = sb.table("profiles").select("*", count="exact")

    if search:
        query = query.or_(f"email.ilike.%{search}%,full_name.ilike.%{search}%")
    if role:
        query = query.eq("role", role)
    if tier:
        query = query.eq("tier", tier)

    offset = (page - 1) * per_page
    result = (
        query.order("created_at", desc=True)
        .range(offset, offset + per_page - 1)
        .execute()
    )

    return {
        "users": result.data,
        "total": result.count,
        "page": page,
        "per_page": per_page,
    }


@router.get("/users/{user_id}")
async def get_user(user_id: str, admin: CurrentUser = Depends(require_admin)):
    sb = get_supabase()
    profile = sb.table("profiles").select("*").eq("id", user_id).single().execute()
    if not profile.data:
        raise HTTPException(status_code=404, detail="User not found")

    usage = (
        sb.table("usage_logs")
        .select("*", count="exact")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(10)
        .execute()
    )
    subscription = (
        sb.table("subscriptions")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
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
    sb = get_supabase()
    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    if "role" in updates and updates["role"] not in ("user", "admin"):
        raise HTTPException(status_code=400, detail="Invalid role")
    if "tier" in updates and updates["tier"] not in ("free", "pro", "enterprise"):
        raise HTTPException(status_code=400, detail="Invalid tier")

    result = sb.table("profiles").update(updates).eq("id", user_id).execute()
    return {"updated": result.data}


# ── Analytics ────────────────────────────────────────────────


@router.get("/analytics/overview")
async def analytics_overview(admin: CurrentUser = Depends(require_admin)):
    sb = get_supabase()

    total_users = sb.table("profiles").select("id", count="exact").execute()
    active_users = (
        sb.table("profiles")
        .select("id", count="exact")
        .eq("is_active", True)
        .execute()
    )
    pro_users = (
        sb.table("profiles")
        .select("id", count="exact")
        .eq("tier", "pro")
        .execute()
    )
    enterprise_users = (
        sb.table("profiles")
        .select("id", count="exact")
        .eq("tier", "enterprise")
        .execute()
    )
    total_generations = sb.table("usage_logs").select("id", count="exact").execute()

    return {
        "total_users": total_users.count,
        "active_users": active_users.count,
        "pro_users": pro_users.count,
        "enterprise_users": enterprise_users.count,
        "total_generations": total_generations.count,
    }


@router.get("/analytics/usage")
async def analytics_usage(
    days: int = Query(30, ge=1, le=365),
    admin: CurrentUser = Depends(require_admin),
):
    """Return generation data for the last N days."""
    sb = get_supabase()
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

    result = (
        sb.table("usage_logs")
        .select("created_at, mode, tool")
        .gte("created_at", since)
        .order("created_at", desc=False)
        .execute()
    )
    return {"usage": result.data, "days": days}


@router.get("/analytics/tiers")
async def analytics_tiers(admin: CurrentUser = Depends(require_admin)):
    """Breakdown of users by tier."""
    sb = get_supabase()
    free = (
        sb.table("profiles")
        .select("id", count="exact")
        .eq("tier", "free")
        .execute()
    )
    pro = (
        sb.table("profiles")
        .select("id", count="exact")
        .eq("tier", "pro")
        .execute()
    )
    enterprise = (
        sb.table("profiles")
        .select("id", count="exact")
        .eq("tier", "enterprise")
        .execute()
    )

    return {
        "tiers": [
            {"tier": "free", "count": free.count},
            {"tier": "pro", "count": pro.count},
            {"tier": "enterprise", "count": enterprise.count},
        ]
    }
