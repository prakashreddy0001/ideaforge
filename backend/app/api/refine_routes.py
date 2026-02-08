import asyncio

from fastapi import APIRouter, Depends, HTTPException

from app.api.schemas import RefineRequest, RefineResponse
from app.core.auth import get_current_user, CurrentUser
from app.services.prompt_refiner import refine_prompt
from app.services.usage import check_usage_allowed, log_usage

router = APIRouter()


@router.post("/refine", response_model=RefineResponse)
async def refine(req: RefineRequest, user: CurrentUser = Depends(get_current_user)):
    allowed = await asyncio.to_thread(check_usage_allowed, user.id, user.tier)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Monthly generation limit reached for {user.tier} tier. Please upgrade.",
        )

    try:
        result = await asyncio.to_thread(refine_prompt, req.prompt)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Fire-and-forget: log usage without blocking the response
    asyncio.get_event_loop().run_in_executor(
        None, log_usage, user.id, req.prompt[:200], "refine", None
    )
    return result
