import asyncio
import os

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.api.schemas import DesignToCodeResponse
from app.core.auth import get_current_user, CurrentUser
from app.services.design_to_code import generate_code_from_design, SUPPORTED_FORMATS
from app.services.usage import check_usage_allowed, log_usage

router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME_TYPES = {"image/png", "image/jpeg", "image/webp"}
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


@router.post("/design-to-code", response_model=DesignToCodeResponse)
async def design_to_code(
    image: UploadFile = File(...),
    output_format: str = Form(...),
    additional_instructions: str = Form(""),
    user: CurrentUser = Depends(get_current_user),
):
    # Usage limit check
    allowed = await asyncio.to_thread(check_usage_allowed, user.id, user.tier)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Monthly generation limit reached for {user.tier} tier. Please upgrade.",
        )

    # Validate output format
    if output_format not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid output format. Choose: {', '.join(sorted(SUPPORTED_FORMATS))}",
        )

    # Validate MIME type
    content_type = image.content_type or ""
    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image format. Please upload a PNG, JPG, or WEBP file.",
        )

    # Validate file extension
    ext = os.path.splitext(image.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file extension. Please upload a PNG, JPG, or WEBP file.",
        )

    # Read and validate file size
    image_bytes = await image.read()
    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image must be under 10 MB.",
        )

    if not image_bytes:
        raise HTTPException(status_code=400, detail="Image file is empty.")

    # Generate code
    try:
        result = await asyncio.to_thread(
            generate_code_from_design,
            image_bytes,
            content_type,
            output_format,
            additional_instructions,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Fire-and-forget usage log
    asyncio.get_event_loop().run_in_executor(
        None, log_usage, user.id, f"design_to_code:{output_format}", "design_to_code", None
    )

    return result
