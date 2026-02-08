from fastapi import APIRouter, Depends

from app.core.auth import get_current_user, CurrentUser
from app.services.usage import get_monthly_usage, get_tier_limit

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
async def get_me(user: CurrentUser = Depends(get_current_user)):
    """Return the current user's profile and usage stats."""
    used = get_monthly_usage(user.id)
    limit = get_tier_limit(user.tier)
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "tier": user.tier,
        "is_active": user.is_active,
        "usage": {
            "used": used,
            "limit": limit,
            "remaining": max(0, limit - used) if limit != -1 else -1,
        },
    }
