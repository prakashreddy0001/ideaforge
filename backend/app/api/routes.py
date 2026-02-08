from fastapi import APIRouter, Depends, HTTPException

from app.api.schemas import IdeaRequest, IdeaResponse
from app.core.auth import get_current_user, CurrentUser
from app.services.ideation import generate_package
from app.services.usage import check_usage_allowed, log_usage

router = APIRouter()


@router.post("/plan", response_model=IdeaResponse)
async def plan(req: IdeaRequest, user: CurrentUser = Depends(get_current_user)):
    if not check_usage_allowed(user.id, user.tier):
        raise HTTPException(
            status_code=429,
            detail=f"Monthly generation limit reached for {user.tier} tier. Please upgrade.",
        )

    try:
        result = generate_package(req)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    log_usage(user.id, req.idea[:200], req.mode, req.tool)
    return result
