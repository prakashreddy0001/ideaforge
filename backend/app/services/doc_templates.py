"""Rich documentation generators.

Produces 5 detailed documentation outputs: readme, api_spec, data_model,
env_setup, and deployment_guide.
"""

from typing import Dict, Optional, Set

from app.services.feature_detection import FEATURE_DESCRIPTIONS
from app.services.stack_selection import StackChoice


def _domain_entity_names(domain: Optional[Dict]) -> str:
    if not domain or "entities" not in domain:
        return ""
    return ", ".join(e["name"] for e in domain["entities"])


def _readme(idea: str, flags: Set[str], stack: StackChoice, domain: Optional[Dict] = None) -> str:
    stack_rows = "\n".join(
        f"| {k.replace('_', ' ').title()} | {v} |"
        for k, v in stack.to_dict().items()
        if v != "None"
    )
    feature_list = "\n".join(
        f"- **{f.replace('_', ' ').title()}** — {FEATURE_DESCRIPTIONS.get(f, f)}"
        for f in sorted(flags)
    )
    if not feature_list:
        feature_list = "- Standard CRUD application"

    return f"""# Project Name

> {idea}

---

## Architecture Overview

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Frontend   │─────▶│   Backend    │─────▶│  Database    │
│  (Next.js)   │      │  (FastAPI)   │      │ (PostgreSQL) │
└──────────────┘      └──────┬───────┘      └──────────────┘
                             │
                      ┌──────▼───────┐
                      │  External    │
                      │  Services    │
                      │ (AI, Stripe) │
                      └──────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|------------|
{stack_rows}

## Detected Features

{feature_list}

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 16
- Redis 7 (if real-time / caching is used)
- Docker & Docker Compose (recommended)

## Quick Start

```bash
# Clone the repository
git clone <repo-url> && cd <project>

# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # Fill in your keys
alembic upgrade head          # Run migrations
uvicorn app.main:app --reload # Start on http://localhost:8000

# Frontend (new terminal)
cd frontend
npm install
cp .env.local.example .env.local
npm run dev                   # Start on http://localhost:3000
```

Or with Docker Compose:

```bash
docker compose up --build
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/routes/       # HTTP + WebSocket endpoints
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   ├── services/         # Business logic
│   │   ├── core/             # Config, DB, security
│   │   └── middleware/       # Error handling, rate limiting
│   ├── alembic/              # Database migrations
│   ├── tests/                # pytest test suite
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/                  # Next.js App Router pages
│   ├── components/           # React components
│   ├── lib/                  # API client, auth, utilities
│   └── public/               # Static assets
├── docker-compose.yml
└── .github/workflows/ci.yml
```

## Available Scripts

| Command | Description |
|---------|-------------|
| `uvicorn app.main:app --reload` | Start backend (dev) |
| `npm run dev` | Start frontend (dev) |
| `alembic upgrade head` | Run DB migrations |
| `alembic revision --autogenerate -m "msg"` | Create new migration |
| `pytest` | Run backend tests |
| `npm test` | Run frontend tests |
| `npx playwright test` | Run E2E tests |
| `docker compose up --build` | Start everything |

## API Endpoints (summary)

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | /api/auth/register | Create account | Public |
| POST | /api/auth/login | Authenticate | Public |
| POST | /api/auth/refresh | Refresh token | Public |
| GET  | /health | Service health | Public |
{"".join(f"| {ep['method']} | {ep['path']} | {ep.get('description', '')} | {ep.get('auth', 'Authenticated')} |{chr(10)}" for ep in domain.get("api_endpoints", [])) if domain and "api_endpoints" in domain else "| ... | /api/... | Domain endpoints | Authenticated |"}

See **API_REFERENCE.md** for full endpoint documentation.

## Contributing

1. Fork the repository
2. Create a feature branch: ``git checkout -b feature/my-feature``
3. Commit changes: ``git commit -m "Add my feature"``
4. Push: ``git push origin feature/my-feature``
5. Open a Pull Request

## License

MIT
"""


def _api_spec(idea: str, flags: Set[str], stack: StackChoice, domain: Optional[Dict] = None) -> str:
    extra_endpoints = ""
    if "payments" in flags:
        extra_endpoints += """
| POST | /api/checkout | Create Stripe checkout session | Authenticated |
| POST | /api/billing-portal | Open Stripe billing portal | Authenticated |
| GET  | /api/subscription | Current subscription status | Authenticated |
| POST | /api/webhooks/stripe | Stripe webhook receiver | Public (signature verified) |
"""
    if "ai" in flags:
        extra_endpoints += """
| POST | /api/ai/generate | Generate AI response | Authenticated |
| POST | /api/ai/stream | Stream AI response (SSE) | Authenticated |
"""
    if "file_upload" in flags:
        extra_endpoints += """
| POST | /api/uploads/presign | Get presigned upload URL | Authenticated |
| POST | /api/uploads/confirm | Confirm completed upload | Authenticated |
| DELETE | /api/uploads/{id} | Delete uploaded file | Authenticated |
"""
    if "search" in flags:
        extra_endpoints += """
| GET  | /api/search | Full-text search across entities | Authenticated |
"""
    if "realtime" in flags:
        extra_endpoints += """
| WS   | /ws?token=<jwt> | WebSocket connection | Authenticated (token in query) |
"""

    return f"""## API Reference

### Base URL
- Development: ``http://localhost:8000``
- Production: ``https://api.<your-domain>.com``

### Authentication
All authenticated endpoints require:
```
Authorization: Bearer <access_token>
```
Obtain tokens via ``POST /api/auth/login``.

### Standard Response Envelope

**Success (single item):**
```json
{{
  "id": "uuid",
  "field": "value",
  "created_at": "2024-01-01T00:00:00Z"
}}
```

**Success (list with pagination):**
```json
{{
  "items": [...],
  "total": 100,
  "page": 1,
  "per_page": 20,
  "pages": 5
}}
```

**Error:**
```json
{{
  "detail": "Human-readable error message",
  "code": "MACHINE_READABLE_CODE"
}}
```

### Pagination
Use query params: ``?page=1&per_page=20`` (max 100).

### Rate Limiting
- Authenticated: 100 requests / minute
- Unauthenticated: 20 requests / minute
- Headers: ``X-RateLimit-Limit``, ``X-RateLimit-Remaining``, ``X-RateLimit-Reset``

### Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | /api/auth/register | Create account | Public |
| POST | /api/auth/login | Authenticate, return tokens | Public |
| POST | /api/auth/refresh | Refresh access token | Public |
| POST | /api/auth/logout | Invalidate refresh token | Authenticated |
| POST | /api/auth/forgot-password | Send password reset email | Public |
| POST | /api/auth/reset-password | Reset password with token | Public |
| GET  | /health | Service health check | Public |
{extra_endpoints}
{"".join(f"| {ep['method']} | {ep['path']} | {ep.get('description', '')} | {ep.get('auth', 'Authenticated')} |{chr(10)}" for ep in domain.get("api_endpoints", [])) if domain and "api_endpoints" in domain else "_Domain-specific CRUD endpoints should be added for each core entity._"}

### Endpoint Details

#### POST /api/auth/register
**Request:**
```json
{{
  "email": "user@example.com",
  "password": "securePassword123!",
  "name": "Jane Doe"
}}
```
**Response (201):**
```json
{{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "user": {{
    "id": "uuid",
    "email": "user@example.com",
    "name": "Jane Doe"
  }}
}}
```
**Errors:** 400 (validation), 409 (email exists)

#### POST /api/auth/login
**Request:**
```json
{{
  "email": "user@example.com",
  "password": "securePassword123!"
}}
```
**Response (200):** Same as register
**Errors:** 401 (invalid credentials), 429 (rate limited)
"""


def _data_model(idea: str, flags: Set[str], stack: StackChoice, domain: Optional[Dict] = None) -> str:
    extra = ""
    if "payments" in flags:
        extra += """
### Subscription
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK, default gen_random_uuid() |
| user_id | UUID | FK → users.id ON DELETE CASCADE |
| stripe_customer_id | VARCHAR(255) | NOT NULL, UNIQUE |
| stripe_subscription_id | VARCHAR(255) | UNIQUE |
| status | VARCHAR(50) | NOT NULL (active/past_due/canceled/trialing) |
| plan | VARCHAR(50) | NOT NULL |
| current_period_end | TIMESTAMPTZ | |
| created_at | TIMESTAMPTZ | DEFAULT now() |
| updated_at | TIMESTAMPTZ | |

**Indexes:** (user_id), (stripe_customer_id), (stripe_subscription_id)
"""
    if "file_upload" in flags:
        extra += """
### Upload
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK, default gen_random_uuid() |
| user_id | UUID | FK → users.id ON DELETE CASCADE |
| file_key | VARCHAR(500) | NOT NULL, UNIQUE |
| original_name | VARCHAR(255) | NOT NULL |
| content_type | VARCHAR(100) | NOT NULL |
| size_bytes | BIGINT | NOT NULL |
| entity_type | VARCHAR(100) | (polymorphic) |
| entity_id | UUID | (polymorphic) |
| status | VARCHAR(20) | DEFAULT 'pending' |
| created_at | TIMESTAMPTZ | DEFAULT now() |

**Indexes:** (user_id), (entity_type, entity_id), (file_key)
"""
    if "multi_tenancy" in flags:
        extra += """
### Organization
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK, default gen_random_uuid() |
| name | VARCHAR(255) | NOT NULL |
| slug | VARCHAR(100) | NOT NULL, UNIQUE |
| owner_id | UUID | FK → users.id |
| created_at | TIMESTAMPTZ | DEFAULT now() |

### OrgMembership
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| org_id | UUID | FK → organizations.id ON DELETE CASCADE |
| user_id | UUID | FK → users.id ON DELETE CASCADE |
| role | VARCHAR(50) | DEFAULT 'member' |
| created_at | TIMESTAMPTZ | DEFAULT now() |

**Indexes:** (org_id, user_id) UNIQUE
"""

    return f"""## Data Model

### Entity-Relationship Overview

```
users ─── 1:N ─── {_domain_entity_names(domain) if _domain_entity_names(domain) else "[domain entities]"}
  │
  └── 1:1 ─── user_preferences
```
{f"Entities: {_domain_entity_names(domain)}" if _domain_entity_names(domain) else f"_Replace [domain entities] with the actual entities derived from: {idea}_"}

---

### Users
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK, default gen_random_uuid() |
| email | VARCHAR(255) | NOT NULL, UNIQUE |
| password_hash | VARCHAR(255) | NOT NULL |
| name | VARCHAR(255) | NOT NULL |
| avatar_url | VARCHAR(500) | |
| role | VARCHAR(50) | DEFAULT 'member' |
| is_active | BOOLEAN | DEFAULT true |
| email_verified_at | TIMESTAMPTZ | |
| created_at | TIMESTAMPTZ | DEFAULT now() |
| updated_at | TIMESTAMPTZ | |

**Indexes:** (email) UNIQUE, (role), (created_at DESC)

---

### User Preferences
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| user_id | UUID | FK → users.id ON DELETE CASCADE, UNIQUE |
| timezone | VARCHAR(50) | DEFAULT 'UTC' |
| locale | VARCHAR(10) | DEFAULT 'en' |
| notification_email | BOOLEAN | DEFAULT true |
| notification_push | BOOLEAN | DEFAULT true |
| created_at | TIMESTAMPTZ | DEFAULT now() |
| updated_at | TIMESTAMPTZ | |

---

{"".join(f'''### {ent["name"]} (`{ent.get("table_name", ent["name"].lower() + "s")}`)
_{ent.get("description", "")}_

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK, gen_random_uuid() |
| user_id | UUID | FK → users.id |
{"".join(f"| {field} | _inferred_ | Domain field |{chr(10)}" for field in ent.get("fields", []))}| created_at | TIMESTAMPTZ | DEFAULT now() |
| updated_at | TIMESTAMPTZ | Trigger or app-level |

''' for ent in domain.get("entities", [])) if domain and "entities" in domain else '''_Add additional tables for each domain entity specific to the application idea.
Each table should follow this pattern:_

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK, gen_random_uuid() |
| user_id | UUID | FK → users.id |
| [domain fields] | ... | Derived from the idea |
| created_at | TIMESTAMPTZ | DEFAULT now() |
| updated_at | TIMESTAMPTZ | Trigger or app-level |
'''}
{extra}

---

### Migration Notes
- Use Alembic for all schema changes
- Never modify existing migrations; create new ones
- Test migrations: ``alembic upgrade head`` then ``alembic downgrade -1`` then ``alembic upgrade head``
- Seed data script: ``python -m scripts.seed``
"""


def _env_setup(flags: Set[str], stack: StackChoice) -> str:
    extra_vars = ""
    if "payments" in flags:
        extra_vars += """
# --- Stripe ---
STRIPE_SECRET_KEY=sk_test_...           # Stripe secret key (Dashboard → Developers → API keys)
STRIPE_WEBHOOK_SECRET=whsec_...         # Stripe webhook signing secret (Dashboard → Webhooks)
STRIPE_PUBLISHABLE_KEY=pk_test_...      # For frontend (.env.local)
"""
    if "ai" in flags or True:  # Always include since the stack uses OpenAI
        extra_vars += """
# --- AI / LLM ---
OPENAI_API_KEY=sk-...                   # OpenAI API key (platform.openai.com → API keys)
OPENAI_MODEL=gpt-4.1                    # Model to use for AI features
"""
    if "file_upload" in flags:
        extra_vars += """
# --- File Storage ---
AWS_ACCESS_KEY_ID=AKIA...               # AWS IAM key (or R2 access key)
AWS_SECRET_ACCESS_KEY=...               # AWS IAM secret
AWS_S3_BUCKET=my-app-uploads            # S3 bucket name
AWS_S3_REGION=us-east-1                 # Bucket region
CDN_BASE_URL=https://cdn.example.com    # CloudFront / CDN URL
"""
    if "search" in flags:
        extra_vars += """
# --- Search ---
MEILISEARCH_URL=http://localhost:7700   # Meilisearch instance URL
MEILISEARCH_MASTER_KEY=masterKey123     # Meilisearch master key
"""
    if "notifications" in flags or "payments" in flags:
        extra_vars += """
# --- Email ---
RESEND_API_KEY=re_...                   # Resend API key (resend.com → API Keys)
EMAIL_FROM=noreply@yourdomain.com       # Sender email address
"""

    return f"""## Environment Setup

### Backend (`backend/.env`)

```dotenv
# --- Application ---
APP_ENV=development                     # development | staging | production
DEBUG=true                              # Enable debug mode (never true in production)
SECRET_KEY=change-me-to-random-string   # Used for JWT signing (generate: openssl rand -hex 32)

# --- Database ---
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/myapp
DATABASE_POOL_SIZE=10                   # Connection pool size
DATABASE_MAX_OVERFLOW=20                # Max overflow connections

# --- Redis ---
REDIS_URL=redis://localhost:6379/0      # Redis connection URL (if caching/realtime)

# --- Auth ---
JWT_SECRET=change-me-to-random-string   # JWT signing secret (generate: openssl rand -hex 32)
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15      # Access token lifetime
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7         # Refresh token lifetime

# --- CORS ---
CORS_ALLOW_ORIGINS=["http://localhost:3000"]  # Comma-separated allowed origins
{extra_vars}
# --- Monitoring ---
SENTRY_DSN=                             # Sentry DSN (sentry.io → Project Settings)
LOG_LEVEL=INFO                          # DEBUG | INFO | WARNING | ERROR
```

### Frontend (`frontend/.env.local`)

```dotenv
NEXT_PUBLIC_API_URL=http://localhost:8000   # Backend API URL
NEXT_PUBLIC_APP_NAME=MyApp                 # App display name
NEXT_PUBLIC_APP_URL=http://localhost:3000   # Frontend URL (for OAuth callbacks)
{"NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_..." if "payments" in flags else ""}
```

### How to Obtain API Keys

| Service | Where to Get Key |
|---------|-----------------|
| PostgreSQL | Local install or managed (Supabase, Neon, Railway) |
| Redis | Local install or managed (Upstash, Redis Cloud) |
| OpenAI | https://platform.openai.com/api-keys |
{"| Stripe | https://dashboard.stripe.com/test/apikeys |" if "payments" in flags else ""}
{"| Resend | https://resend.com/api-keys |" if "notifications" in flags or "payments" in flags else ""}
{"| AWS S3 | https://console.aws.amazon.com/iam |" if "file_upload" in flags else ""}
{"| Meilisearch | Self-hosted or https://www.meilisearch.com/cloud |" if "search" in flags else ""}
| Sentry | https://sentry.io → Create Project |

### Development vs Production

| Variable | Development | Production |
|----------|-------------|------------|
| APP_ENV | development | production |
| DEBUG | true | **false** |
| DATABASE_URL | localhost | Managed DB URL (SSL) |
| CORS_ALLOW_ORIGINS | localhost:3000 | Your domain |
| SENTRY_DSN | (empty) | Real DSN |
"""


def _deployment_guide(flags: Set[str], stack: StackChoice) -> str:
    return f"""## Deployment Guide

### Local Development (Docker Compose)

```bash
# Start all services
docker compose up --build

# Stop all services
docker compose down

# Reset database
docker compose down -v  # Removes volumes
docker compose up --build
```

### Staging Deployment Checklist

- [ ] Set all environment variables in hosting platform
- [ ] Ensure ``APP_ENV=staging`` and ``DEBUG=false``
- [ ] Run database migrations: ``alembic upgrade head``
- [ ] Verify health endpoint: ``curl https://api-staging.example.com/health``
- [ ] Run smoke tests against staging API
- [ ] Verify CORS allows staging frontend domain
- [ ] Verify email sending works (check Resend dashboard)
- [ ] Test authentication flow end-to-end
{"- [ ] Test Stripe webhook delivery (use Stripe CLI for testing)" if "payments" in flags else ""}

### Production Deployment Checklist

- [ ] All staging checklist items pass
- [ ] ``APP_ENV=production``, ``DEBUG=false``
- [ ] Strong ``SECRET_KEY`` and ``JWT_SECRET`` (256-bit random)
- [ ] Database connection uses SSL: ``?sslmode=require``
- [ ] CORS strictly limited to production domain
- [ ] Rate limiting configured and tested
- [ ] Sentry DSN configured for error tracking
- [ ] Database backups configured (daily, 30-day retention)
- [ ] SSL/TLS certificate active (auto-renewed)
- [ ] CDN configured for frontend assets
- [ ] Monitoring dashboards created
{"- [ ] Stripe webhook endpoint set to production URL" if "payments" in flags else ""}
{"- [ ] Search index populated with production data" if "search" in flags else ""}

### Database Migration Procedure

```bash
# Create a new migration
alembic revision --autogenerate -m "describe the change"

# Review the generated migration file
# Then apply:
alembic upgrade head

# If something goes wrong:
alembic downgrade -1
```

**In production**: Migrations run as a pre-deploy step in CI/CD.
Never run migrations manually in production.

### Rollback Procedure

1. **Application rollback**: Redeploy previous container image tag
2. **Database rollback**: ``alembic downgrade -1`` (only if migration was the issue)
3. **Verify**: Check health endpoint and run smoke tests
4. **Communicate**: Update status page, notify team

### Monitoring Setup

| Tool | Purpose | Setup |
|------|---------|-------|
| Sentry | Error tracking | Add SENTRY_DSN env var |
| Health endpoint | Uptime monitoring | Point uptime monitor at /health |
| Structured logs | Debugging | Use structlog, ship to log aggregator |
{"| Prometheus + Grafana | Metrics | Deploy alongside app, scrape /metrics |" if "analytics" in flags else ""}

### Infrastructure ({stack.infra})

Refer to the ``deployment_config`` prompt for complete Docker, CI/CD, and
infrastructure-as-code files.
"""


# ===================================================================
# MVP DOCS (lean)
# ===================================================================

def _mvp_readme(idea: str, stack: StackChoice) -> str:
    return f"""# Project Name

> {idea}

## Tech Stack
- Frontend: {stack.frontend}
- Backend: {stack.backend}
- Database: {stack.database}

## Quick Start

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

Backend: http://localhost:8000 | Frontend: http://localhost:3000
"""


def _mvp_env(flags: Set[str]) -> str:
    extra = ""
    if "ai" in flags:
        extra += "OPENAI_API_KEY=sk-...                   # platform.openai.com\n"
    return f"""## Environment Variables

### Backend (`.env`)
```dotenv
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/myapp
JWT_SECRET=change-me           # openssl rand -hex 32
CORS_ALLOW_ORIGINS=["http://localhost:3000"]
{extra}```

### Frontend (`.env.local`)
```dotenv
NEXT_PUBLIC_API_URL=http://localhost:8000
```
"""


# ===================================================================
# PUBLIC API
# ===================================================================

def build_doc_pack(
    idea: str,
    flags: Set[str],
    stack: StackChoice,
    target_users: Optional[str] = None,
    mode: str = "production",
    domain: Optional[Dict] = None,
    tool=None,
) -> Dict[str, str]:
    """Build the documentation dictionary.

    - mode="mvp": 2 lean docs (readme, env_setup)
    - mode="production": 5 full docs
    - tool: optional ToolProfile for tool-specific doc adaptations
    """
    # ── Tool-specific docs ──
    if tool is not None:
        slug = tool.slug
        if slug == "lovable":
            return _lovable_docs(idea, flags, stack, domain, mode)
        elif slug == "base44":
            return _base44_docs(idea, flags, stack, domain, mode)
        elif slug == "replit":
            return _replit_docs(idea, flags, stack, domain, mode)
        # claude_code falls through to default

    if mode == "mvp":
        return {
            "readme": _mvp_readme(idea, stack),
            "env_setup": _mvp_env(flags),
        }

    return {
        "readme": _readme(idea, flags, stack, domain),
        "api_spec": _api_spec(idea, flags, stack, domain),
        "data_model": _data_model(idea, flags, stack, domain),
        "env_setup": _env_setup(flags, stack),
        "deployment_guide": _deployment_guide(flags, stack),
    }


# ===================================================================
# TOOL-SPECIFIC DOCS
# ===================================================================

def _lovable_docs(idea: str, flags: Set[str], stack: StackChoice, domain: Optional[Dict], mode: str) -> Dict[str, str]:
    """Docs tailored for Lovable (Supabase-based)."""
    entities = _domain_entity_names(domain)
    docs: Dict[str, str] = {}

    docs["readme"] = f"""# Project Name

> {idea}

## Tech Stack (Lovable)
- **Frontend:** React 18 + Vite + Tailwind CSS + shadcn/ui
- **Backend:** Supabase (PostgreSQL, Auth, Edge Functions, Storage, Realtime)
- **Hosting:** Lovable auto-deploy

## Getting Started
1. Open project in Lovable (lovable.dev)
2. Connect your Supabase project (Project Settings → Integrations → Supabase)
3. Run the SQL migration in Supabase SQL Editor
4. Deploy via Lovable's built-in hosting

## Supabase Setup
1. Create a Supabase project at https://supabase.com
2. Copy the SQL from the `database_schema` prompt into the SQL Editor
3. Enable Row-Level Security on all tables
4. Configure Auth providers (email/password + OAuth if needed)
{f'{chr(10)}## Entities: {entities}' if entities else ''}

## Environment Variables
Lovable manages most config automatically. Set these in Supabase:
- `SUPABASE_URL` — auto-configured by Lovable
- `SUPABASE_ANON_KEY` — auto-configured by Lovable
{"- `STRIPE_SECRET_KEY` — set in Supabase Edge Function secrets" if "payments" in flags else ""}
{"- `OPENAI_API_KEY` — set in Supabase Edge Function secrets" if "ai" in flags else ""}
"""

    docs["supabase_setup"] = f"""## Supabase Configuration Guide

### 1. Create Project
- Go to https://supabase.com → New Project
- Choose region closest to your users
- Save the project URL and anon key

### 2. Database
- Paste the SQL from `database_schema` prompt into SQL Editor
- Verify all tables created with RLS enabled

### 3. Authentication
- Dashboard → Authentication → Providers
- Enable Email provider (enabled by default)
- Configure email templates (optional)

### 4. Storage (if needed)
- Dashboard → Storage → Create bucket
- Set RLS policies on buckets

### 5. Edge Functions (if needed)
- Install Supabase CLI: `npm install -g supabase`
- Create function: `supabase functions new my-function`
- Deploy: `supabase functions deploy my-function`
"""

    return docs


def _replit_docs(idea: str, flags: Set[str], stack: StackChoice, domain: Optional[Dict], mode: str) -> Dict[str, str]:
    """Docs tailored for Replit Agent."""
    entities = _domain_entity_names(domain)
    docs: Dict[str, str] = {}

    docs["readme"] = f"""# Project Name

> {idea}

## Tech Stack (Replit)
- **Frontend:** React 18 + Vite + Tailwind CSS + shadcn/ui
- **Backend:** Node.js 20 + Express 4
- **Database:** PostgreSQL 16 + Prisma ORM
- **Hosting:** Replit Deployments

## Getting Started
1. Open project in Replit
2. Click "Run" — Replit installs dependencies and starts the app
3. Set environment variables in Replit Secrets (padlock icon)

## Environment Variables (Replit Secrets)
| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection URL (auto-set by Replit) |
| `JWT_SECRET` | Secret for JWT signing (generate: `openssl rand -hex 32`) |
{"| `STRIPE_SECRET_KEY` | Stripe API key |" if "payments" in flags else ""}
{"| `OPENAI_API_KEY` | OpenAI API key |" if "ai" in flags else ""}
{f'{chr(10)}## Entities: {entities}' if entities else ''}

## Deployment
- Click "Deploy" in the Replit workspace
- Replit handles hosting, SSL, and auto-restart
"""

    if mode == "production":
        docs["api_spec"] = _api_spec(idea, flags, stack, domain)

    return docs


def _base44_docs(idea: str, flags: Set[str], stack: StackChoice, domain: Optional[Dict], mode: str) -> Dict[str, str]:
    """Docs tailored for Base44 (no-code platform)."""
    entities = _domain_entity_names(domain)
    docs: Dict[str, str] = {}

    docs["readme"] = f"""# Project Name

> {idea}

## Platform: Base44 (base44.com)
Base44 is a data-first AI app builder. No code is needed — define entities, pages, and workflows.

## Getting Started
1. Create a new app at https://base44.com
2. Define entities using the `entity_design` prompt
3. Create pages using the `page_design` prompt
4. Configure user roles and permissions
5. Publish the app
{f'{chr(10)}## Entities: {entities}' if entities else ''}

## Key Concepts
- **Entities**: Data models with fields, types, and relations
- **Pages**: UI views tied to entities (List, Detail, Form, Dashboard)
- **Workflows**: Automation rules triggered by data events
- **Roles**: User access control per entity and page
"""

    docs["entity_reference"] = f"""## Entity Reference
{f'Entities to create: {entities}' if entities else 'Define entities based on the app idea.'}

### Field Types
| Type | Description | Example |
|------|-------------|---------|
| Text | Short text | Name, title |
| LongText | Multi-line text | Description, notes |
| Number | Integer or decimal | Price, quantity |
| Boolean | True/false | Is active, is published |
| Date | Date only | Due date |
| DateTime | Date + time | Created at |
| Select | Single choice | Status, priority |
| Relation | Link to entity | Author, category |
| Image | Image upload | Avatar, photo |
| File | File upload | Document, attachment |
"""

    return docs
