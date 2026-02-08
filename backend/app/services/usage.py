from datetime import datetime, timezone

from app.core.supabase_client import get_supabase


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
    """Fetch the monthly generation limit for a tier."""
    sb = get_supabase()
    result = (
        sb.table("tier_limits")
        .select("monthly_generations")
        .eq("tier", tier)
        .single()
        .execute()
    )
    if result.data:
        return result.data["monthly_generations"]
    return 5


def check_usage_allowed(user_id: str, tier: str) -> bool:
    """Return True if the user can generate, False if rate-limited."""
    limit = get_tier_limit(tier)
    if limit == -1:
        return True
    used = get_monthly_usage(user_id)
    return used < limit


def log_usage(user_id: str, idea_summary: str, mode: str, tool: str | None):
    """Record a generation in usage_logs."""
    sb = get_supabase()
    sb.table("usage_logs").insert({
        "user_id": user_id,
        "action": "generation",
        "idea_summary": idea_summary[:200],
        "mode": mode,
        "tool": tool,
    }).execute()
