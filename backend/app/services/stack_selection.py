"""Tech-stack selection driven by detected feature flags."""

from dataclasses import dataclass, asdict
from typing import Dict, Set


@dataclass
class StackChoice:
    frontend: str
    frontend_ui: str
    backend: str
    database: str
    cache: str
    infra: str
    auth: str
    ai: str
    search: str
    file_storage: str
    email: str
    monitoring: str
    testing: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


def choose_stack(flags: Set[str]) -> StackChoice:
    """Return a fully-populated StackChoice based on *flags*."""

    # --- Frontend ---
    frontend = "Next.js 14 (App Router) + Tailwind CSS 3"
    frontend_ui = "shadcn/ui + Radix primitives"
    if "mobile" in flags:
        frontend += " (+ React Native for mobile)"

    # --- Backend ---
    backend = "FastAPI 0.115 + Uvicorn (Python 3.11+)"

    # --- Database ---
    database = "PostgreSQL 16 + SQLAlchemy 2.0 (async) + Alembic"
    if "ai" in flags:
        database += " + pgvector"
    if "analytics" in flags:
        database += " + TimescaleDB"

    # --- Cache ---
    cache = "None"
    if "realtime" in flags or "scheduling" in flags:
        cache = "Redis 7 (pub/sub + caching)"
    elif len(flags) >= 3:
        cache = "Redis 7 (caching layer)"

    # --- Search ---
    search = "None"
    if "search" in flags:
        search = "Meilisearch (lightweight full-text search)"
        if "analytics" in flags or len(flags) >= 6:
            search = "Elasticsearch 8 (advanced search + analytics)"

    # --- File storage ---
    file_storage = "None"
    if "file_upload" in flags:
        file_storage = "AWS S3 (via boto3) + CloudFront CDN"
    elif "social" in flags:
        file_storage = "Cloudflare R2 (avatars + media)"

    # --- Email ---
    email = "None"
    if "notifications" in flags or "payments" in flags:
        email = "Resend (transactional email)"
    elif "auth_advanced" in flags or "scheduling" in flags:
        email = "Resend (transactional email)"

    # --- Infrastructure ---
    if "realtime" in flags:
        infra = "Docker + Render (persistent WebSocket support)"
    elif len(flags) >= 5:
        infra = "Docker + AWS ECS (scalable)"
    else:
        infra = "Docker + Fly.io (simple deploy)"

    # --- Auth ---
    if "auth_advanced" in flags:
        auth = "Auth.js (NextAuth) + custom RBAC middleware"
    elif "payments" in flags or "multi_tenancy" in flags:
        auth = "Auth.js (NextAuth) with JWT sessions"
    else:
        auth = "Clerk (managed auth)"

    # --- AI ---
    ai = "OpenAI GPT-4.1 (via openai SDK)"
    if "ai" in flags:
        ai = "OpenAI GPT-4.1 + Embeddings API + LangChain"

    # --- Monitoring ---
    monitoring = "Sentry (errors) + Structured logging (structlog)"
    if "analytics" in flags or len(flags) >= 5:
        monitoring = "Sentry (errors) + Prometheus + Grafana + structlog"

    # --- Testing ---
    testing = "pytest + httpx (backend) · Playwright (E2E) · Jest + React Testing Library (frontend)"

    return StackChoice(
        frontend=frontend,
        frontend_ui=frontend_ui,
        backend=backend,
        database=database,
        cache=cache,
        infra=infra,
        auth=auth,
        ai=ai,
        search=search,
        file_storage=file_storage,
        email=email,
        monitoring=monitoring,
        testing=testing,
    )
