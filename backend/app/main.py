import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as plan_router
from app.api.auth_routes import router as auth_router
from app.api.refine_routes import router as refine_router
from app.api.admin_routes import router as admin_router
from app.api.stripe_routes import router as stripe_router
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Build CORS origins: merge config list + frontend_url for safety
_origins = list(settings.cors_allow_origins)
if settings.frontend_url and settings.frontend_url not in _origins:
    _origins.append(settings.frontend_url)
logger.info("CORS allow_origins: %s", _origins)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("IdeaForge API starting up")
    yield
    logger.info("IdeaForge API shutting down")


app = FastAPI(title="IdeaForge API", version="0.3.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(plan_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(refine_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(stripe_router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}
