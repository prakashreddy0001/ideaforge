import asyncio
import logging
import time
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from app.core.supabase_client import get_supabase

logger = logging.getLogger(__name__)

security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)

_profile_cache: dict = {}
_PROFILE_CACHE_TTL = 300  # seconds


class CurrentUser(BaseModel):
    id: str
    email: str
    role: str
    tier: str
    is_active: bool


def _verify_token(token: str):
    """Verify token via Supabase Auth — no manual JWT decoding needed."""
    sb = get_supabase()
    return sb.auth.get_user(token)


def _fetch_profile(user_id: str) -> Optional[dict]:
    sb = get_supabase()
    result = sb.table("profiles").select("*").eq("id", user_id).single().execute()
    return result.data


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    token = credentials.credentials

    # Let Supabase verify the token (handles any algorithm)
    try:
        auth_response = await asyncio.to_thread(_verify_token, token)
        supabase_user = auth_response.user
    except Exception as e:
        logger.error(f"Supabase auth failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    if not supabase_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = supabase_user.id

    # Check profile cache
    now = time.monotonic()
    cached = _profile_cache.get(user_id)
    if cached:
        user, ts = cached
        if now - ts < _PROFILE_CACHE_TTL:
            return user

    profile = await asyncio.to_thread(_fetch_profile, user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    if not profile.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    user = CurrentUser(
        id=profile["id"],
        email=profile["email"],
        role=profile["role"],
        tier=profile["tier"],
        is_active=profile["is_active"],
    )
    _profile_cache[user_id] = (user, now)
    return user


async def require_admin(
    user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
) -> Optional[CurrentUser]:
    if credentials is None:
        return None
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
