from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as plan_router
from app.api.auth_routes import router as auth_router

from app.api.admin_routes import router as admin_router
from app.core.config import settings

app = FastAPI(title="IdeaForge API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(plan_router, prefix="/api")
app.include_router(auth_router, prefix="/api")

app.include_router(admin_router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}
