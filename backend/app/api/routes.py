from fastapi import APIRouter, HTTPException

from app.api.schemas import IdeaRequest, IdeaResponse
from app.services.ideation import generate_package

router = APIRouter()


@router.post("/plan", response_model=IdeaResponse)
async def plan(req: IdeaRequest):
    try:
        return generate_package(req)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
