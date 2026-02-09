import logging
import time
from datetime import datetime, timezone
from typing import Optional

from app.core.supabase_client import get_supabase

logger = logging.getLogger(__name__)

# Tier limits rarely change — cache for 1 hour instead of 5 min
_tier_cache: dict = {}
_TIER_CACHE_TTL = 3600


def get_monthly_usage(user_id: str) -> int:
    """Count generations in the current calendar month."""
    sb = get_supabase()
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    result = (
        sb.table("usage_logs")
        .select("id", count="exact")
        .eq("user_id", user_id)
        .eq("action", "generation")
        .gte("created_at", month_start.isoformat())
        .execute()
    )
    return result.count or 0


def get_tier_limit(tier: str) -> int:
    """Fetch the monthly generation limit for a tier (cached for 1 hour)."""
    now = time.monotonic()
    cached = _tier_cache.get(tier)
    if cached:
        value, ts = cached
        if now - ts < _TIER_CACHE_TTL:
            return value

    sb = get_supabase()
    result = (
        sb.table("tier_limits")
        .select("monthly_generations")
        .eq("tier", tier)
        .single()
        .execute()
    )
    value = result.data["monthly_generations"] if result.data else 5
    _tier_cache[tier] = (value, now)
    return value


def check_usage_allowed(user_id: str, tier: str) -> bool:
    """Return True if the user can generate, False if rate-limited."""
    limit = get_tier_limit(tier)
    if limit == -1:
        return True
    used = get_monthly_usage(user_id)
    return used < limit


def log_usage(user_id: str, idea_summary: str, mode: str, tool: Optional[str]):
    """Record a generation in usage_logs."""
    try:
        sb = get_supabase()
        sb.table("usage_logs").insert({
            "user_id": user_id,
            "action": "generation",
            "idea_summary": idea_summary[:200],
            "mode": mode,
            "tool": tool,
        }).execute()
    except Exception:
        logger.exception("Failed to log usage for user %s", user_id)
