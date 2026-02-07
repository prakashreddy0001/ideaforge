"""Heavy, self-contained prompt templates.

Every prompt returned by ``build_prompt_pack`` is designed to be copy-pasted
straight into an AI code-generation assistant and produce complete,
production-grade code with no placeholders or TODOs.
"""

from typing import Dict, List, Optional, Set

from app.services.stack_selection import StackChoice


# ---------------------------------------------------------------------------
# Domain context formatters — turn LLM-extracted domain data into prompt text
# ---------------------------------------------------------------------------

def _domain_entities_block(domain: Optional[Dict]) -> str:
    """Render domain entities as a structured block for prompts."""
    if not domain or "entities" not in domain:
        return ""
    lines = ["\n## Domain Entities (build ALL of these)\n"]
    for ent in domain["entities"]:
        fields = ", ".join(ent.get("fields", []))
        lines.append(f"- **{ent['name']}** (`{ent.get('table_name', ent['name'].lower() + 's')}`): "
                      f"{ent.get('description', '')}  \n  Fields: {fields}")
    return "\n".join(lines)


def _domain_endpoints_block(domain: Optional[Dict]) -> str:
    """Render domain API endpoints as a table for prompts."""
    if not domain or "api_endpoints" not in domain:
        return ""
    lines = ["\n## API Endpoints (implement ALL of these)\n",
             "| Method | Path | Description | Auth |",
             "|--------|------|-------------|------|"]
    for ep in domain["api_endpoints"]:
        lines.append(f"| {ep['method']} | {ep['path']} | {ep.get('description', '')} | {ep.get('auth', 'authenticated')} |")
    return "\n".join(lines)


def _domain_pages_block(domain: Optional[Dict]) -> str:
    """Render frontend pages as a list for prompts."""
    if not domain or "pages" not in domain:
        return ""
    lines = ["\n## Pages to Build (implement ALL of these)\n"]
    for pg in domain["pages"]:
        lines.append(f"- **{pg['name']}** (`{pg.get('path', '')}`): {pg.get('description', '')}")
    return "\n".join(lines)


def _domain_workflows_block(domain: Optional[Dict]) -> str:
    """Render user workflows for prompts."""
    if not domain or "workflows" not in domain:
        return ""
    lines = ["\n## Key User Workflows\n"]
    for i, wf in enumerate(domain["workflows"], 1):
        lines.append(f"{i}. {wf}")
    return "\n".join(lines)


def _domain_dir_backend(domain: Optional[Dict]) -> str:
    """Render backend directory structure with actual entity names."""
    if not domain or "entities" not in domain:
        return """```
backend/
  app/
    __init__.py
    main.py                   # FastAPI app, CORS, middleware, lifespan
    api/
      __init__.py
      routes/
        __init__.py
        auth.py               # POST /register, POST /login, POST /logout, POST /refresh
        [domain_routes].py    # CRUD routes for each core domain entity
        health.py             # GET /health
    models/
      __init__.py
      base.py                 # SQLAlchemy declarative base, common mixins (TimestampMixin)
      user.py                 # User model with hashed password, roles
      [domain_models].py      # One file per domain entity with relationships
    schemas/
      __init__.py
      [domain]_schema.py      # Pydantic request/response schemas per entity
    services/
      __init__.py
      [domain]_service.py     # Business logic per domain entity
    core/
      __init__.py
      config.py               # Pydantic Settings loading from .env
      database.py             # Async engine, session factory, get_db dependency
      security.py             # Password hashing (bcrypt), JWT create/verify, auth dependency
    middleware/
      __init__.py
      error_handler.py        # Global exception handler returning JSON errors
      rate_limiter.py         # Rate-limiting middleware
  alembic/
    env.py
    versions/                 # Initial migration
  alembic.ini
  requirements.txt
  .env.example
```"""

    entities = domain["entities"]
    route_lines = "\n".join(
        f"        {e.get('table_name', e['name'].lower() + 's')}.py"
        f"{'':>8}# CRUD routes for {e['name']}"
        for e in entities
    )
    model_lines = "\n".join(
        f"      {e.get('table_name', e['name'].lower() + 's').rstrip('s')}.py"
        f"{'':>10}# {e['name']} model — {e.get('description', '')}"
        for e in entities
    )
    schema_lines = "\n".join(
        f"      {e.get('table_name', e['name'].lower() + 's').rstrip('s')}_schema.py"
        f"{'':>4}# Pydantic schemas for {e['name']}"
        for e in entities
    )
    service_lines = "\n".join(
        f"      {e.get('table_name', e['name'].lower() + 's').rstrip('s')}_service.py"
        f"{'':>4}# Business logic for {e['name']}"
        for e in entities
    )

    return f"""```
backend/
  app/
    __init__.py
    main.py                   # FastAPI app, CORS, middleware, lifespan
    api/
      __init__.py
      routes/
        __init__.py
        auth.py               # POST /register, POST /login, POST /logout, POST /refresh
{route_lines}
        health.py             # GET /health
    models/
      __init__.py
      base.py                 # SQLAlchemy declarative base, common mixins (TimestampMixin)
      user.py                 # User model with hashed password, roles
{model_lines}
    schemas/
      __init__.py
{schema_lines}
    services/
      __init__.py
{service_lines}
    core/
      __init__.py
      config.py               # Pydantic Settings loading from .env
      database.py             # Async engine, session factory, get_db dependency
      security.py             # Password hashing (bcrypt), JWT create/verify, auth dependency
    middleware/
      __init__.py
      error_handler.py        # Global exception handler returning JSON errors
      rate_limiter.py         # Rate-limiting middleware
  alembic/
    env.py
    versions/                 # Initial migration
  alembic.ini
  requirements.txt
  .env.example
```"""


def _domain_dir_frontend(domain: Optional[Dict]) -> str:
    """Render frontend directory structure with actual page names."""
    if not domain or "pages" not in domain:
        return """```
frontend/
  app/
    layout.js                 # Root layout: fonts, metadata, global providers
    page.js                   # Landing / home page
    globals.css               # Global styles + Tailwind imports
    (auth)/
      login/page.js           # Login form
      register/page.js        # Registration form
    (dashboard)/
      layout.js               # Authenticated layout: sidebar, header, auth guard
      page.js                 # Main dashboard / home
      [domain]/page.js        # Pages for each core domain feature
      settings/page.js        # User settings / profile
    not-found.js              # 404 page
  components/
    ui/                       # Reusable UI primitives (Button, Input, Card, Modal, etc.)
    forms/                    # Domain-specific form components
    layouts/                  # Sidebar, Header, Footer
  lib/
    api-client.js             # Typed fetch wrapper: handles auth headers, errors, refresh
    auth-context.js           # AuthProvider, useAuth hook, login/logout/register functions
    utils.js                  # Formatters, classname helpers
  public/
    favicon.ico
  next.config.js
  tailwind.config.js
  jsconfig.json (or tsconfig.json)
```"""

    pages = domain["pages"]
    page_lines = "\n".join(
        f"      {pg.get('path', '/' + pg['name'].lower().replace(' ', '-')).lstrip('/').split('/')[-1]}/page.js"
        f"{'':>6}# {pg['name']} — {pg.get('description', '')}"
        for pg in pages
        if pg.get("path", "").startswith("/dashboard") or not pg.get("path", "").startswith("/")
    )

    return f"""```
frontend/
  app/
    layout.js                 # Root layout: fonts, metadata, global providers
    page.js                   # Landing / home page
    globals.css               # Global styles + Tailwind imports
    (auth)/
      login/page.js           # Login form
      register/page.js        # Registration form
    (dashboard)/
      layout.js               # Authenticated layout: sidebar, header, auth guard
      page.js                 # Main dashboard / home
{page_lines}
      settings/page.js        # User settings / profile
    not-found.js              # 404 page
  components/
    ui/                       # Reusable UI primitives (Button, Input, Card, Modal, etc.)
    forms/                    # Domain-specific form components
    layouts/                  # Sidebar, Header, Footer
  lib/
    api-client.js             # Typed fetch wrapper: handles auth headers, errors, refresh
    auth-context.js           # AuthProvider, useAuth hook, login/logout/register functions
    utils.js                  # Formatters, classname helpers
  public/
    favicon.ico
  next.config.js
  tailwind.config.js
  jsconfig.json (or tsconfig.json)
```"""


def _entity_names_short(domain: Optional[Dict]) -> str:
    """Return a comma-separated list of entity names, or empty string."""
    if not domain or "entities" not in domain:
        return ""
    return ", ".join(e["name"] for e in domain["entities"])

# ---------------------------------------------------------------------------
# Shared quality footer appended to every prompt
# ---------------------------------------------------------------------------

_QUALITY_FOOTER = """
## Quality Requirements
- All code must be COMPLETE — no TODOs, no placeholders, no "implement here" comments.
- Include proper error handling for every operation that can fail.
- Include input validation for every user-facing input.
- Include proper logging (INFO for business events, ERROR for failures).
- Use type hints (Python) / TypeScript types throughout.
- Follow framework idioms and best practices.

## Output Format
Produce the code as a series of complete files. Precede each file with a comment
showing its path, e.g.:
```
# filepath: backend/app/models/user.py
```
"""


def _stack_block(stack: StackChoice, keys: Optional[List[str]] = None) -> str:
    """Render a subset of the stack as a bullet list for prompt injection."""
    d = stack.to_dict()
    if keys:
        d = {k: v for k, v in d.items() if k in keys}
    return "\n".join(f"- **{k.replace('_', ' ').title()}**: {v}" for k, v in d.items() if v != "None")


# ===================================================================
# CORE PROMPTS (always generated)
# ===================================================================

def _product_requirements(idea: str, target_users: Optional[str], stack: StackChoice, domain: Optional[Dict] = None) -> str:
    domain_section = ""
    if domain:
        entity_list = ", ".join(e["name"] for e in domain.get("entities", []))
        workflow_text = _domain_workflows_block(domain)
        domain_section = f"""
## Domain Model
Core entities to cover in the PRD: {entity_list}
{workflow_text}
"""
    return f"""You are a senior product manager with 12+ years of experience shipping SaaS products.
Write a **complete Product Requirements Document (PRD)** for the application described below.

## Application Idea
{idea}

{f"## Target Users{chr(10)}{target_users}" if target_users else ""}

## Chosen Tech Stack
{_stack_block(stack)}
{domain_section}
## What You Must Include

1. **Problem Statement** — What pain point does this solve? Why now?
2. **User Personas** — Define at least 3 detailed personas with names, roles, goals, and frustrations.
3. **User Stories** — Write at least 15 user stories in Given/When/Then format covering:
   - Core happy-path workflows
   - Edge cases and error states
   - Admin / moderation flows (if applicable)
4. **MVP Feature Set** — Prioritized list (P0 = must-have for launch, P1 = fast-follow, P2 = future).
5. **Acceptance Criteria** — Measurable criteria for each P0 feature.
6. **Non-Functional Requirements** — Performance targets (page load < 2 s, API response < 300 ms), accessibility (WCAG 2.1 AA), SEO, browser support, uptime SLA.
7. **Success Metrics** — 5+ specific KPIs with concrete targets (e.g., "DAU/MAU ratio > 40% within 3 months").
8. **Risks and Mitigations** — At least 5 product risks with mitigation strategies.
9. **Out of Scope** — Explicitly list what is NOT included in the MVP.
{_QUALITY_FOOTER}"""


def _backend_code(idea: str, target_users: Optional[str], flags: Set[str], stack: StackChoice, domain: Optional[Dict] = None) -> str:
    feature_notes = ""
    if "realtime" in flags:
        feature_notes += "\n- Implement WebSocket endpoints for real-time features using FastAPI WebSocket support."
    if "payments" in flags:
        feature_notes += "\n- Integrate Stripe SDK: products, prices, subscriptions, webhook handler, customer portal."
    if "ai" in flags:
        feature_notes += "\n- Integrate OpenAI SDK: chat completions, embeddings. Include prompt versioning and token tracking."
    if "file_upload" in flags:
        feature_notes += "\n- Implement presigned-URL upload flow to S3/R2. Include file-type validation and size limits."
    if "search" in flags:
        feature_notes += "\n- Implement search indexing and query endpoint via Meilisearch/Elasticsearch."
    if "scheduling" in flags:
        feature_notes += "\n- Implement scheduling logic with availability windows, booking conflicts, and reminders."
    if "notifications" in flags:
        feature_notes += "\n- Implement notification service: in-app, email (via Resend), and optional SMS."
    if "multi_tenancy" in flags:
        feature_notes += "\n- Implement tenant isolation: org-scoped models, middleware to inject current tenant."
    if "analytics" in flags:
        feature_notes += "\n- Implement analytics aggregation endpoints for dashboard data."

    dir_structure = _domain_dir_backend(domain)
    endpoints_section = _domain_endpoints_block(domain)
    entities_section = _domain_entities_block(domain)

    if not endpoints_section:
        endpoints_section = """
## API Endpoints (implement ALL)
Design RESTful endpoints for every core entity identified in the idea.
For each endpoint provide:
- HTTP method + path (e.g., POST /api/users)
- Request body schema (Pydantic model)
- Response schema (Pydantic model)
- Auth requirement (public / authenticated / admin)
- HTTP status codes (201 create, 200 read/update, 204 delete, 400/401/403/404/409/422/500)"""

    return f"""You are a senior Python backend engineer specialising in FastAPI.
Produce **COMPLETE, WORKING, PRODUCTION-READY** backend code for the application below.

## Application Idea
{idea}
{f"{chr(10)}Target Users: {target_users}" if target_users else ""}

## Tech Stack (use these exact technologies)
{_stack_block(stack, ["backend", "database", "cache", "auth", "ai", "monitoring"])}
{entities_section}

## Directory Structure (create ALL of these files)
{dir_structure}
{endpoints_section}

For each endpoint provide:
- HTTP method + path
- Request body schema (Pydantic model)
- Response schema (Pydantic model)
- Auth requirement (public / authenticated / admin)
- HTTP status codes (201 create, 200 read/update, 204 delete, 400/401/403/404/409/422/500)
{feature_notes}

## Database Models
- Use SQLAlchemy 2.0 async style with ``mapped_column``.
- Every model MUST have: ``id`` (UUID, PK, default uuid4), ``created_at``, ``updated_at``.
- Define all foreign keys with ON DELETE behaviour.
- Add indexes on columns used in WHERE/ORDER BY clauses.
- Include a ``__repr__`` for debugging.

## Authentication & Authorization
- Implement JWT access + refresh token pattern.
- Hash passwords with bcrypt via passlib.
- Create ``get_current_user`` dependency.
- Protect endpoints that require authentication.
- If roles exist, add role-checking dependency.

## Error Handling
- Custom exception classes: NotFoundError, ConflictError, ForbiddenError.
- Global exception handler returning ``{{"detail": "...", "code": "..."}}`` JSON.
- Never leak stack traces to the client.

## Pagination
- Standard query params: ``?page=1&per_page=20``
- Response shape: ``{{"items": [...], "total": N, "page": N, "per_page": N, "pages": N}}``
{_QUALITY_FOOTER}"""


def _frontend_code(idea: str, target_users: Optional[str], flags: Set[str], stack: StackChoice, domain: Optional[Dict] = None) -> str:
    feature_notes = ""
    if "realtime" in flags:
        feature_notes += "\n- Implement WebSocket client with auto-reconnect for real-time updates."
    if "payments" in flags:
        feature_notes += "\n- Build pricing page, checkout flow with Stripe Elements, and subscription management page."
    if "ai" in flags:
        feature_notes += "\n- Build AI interaction UI: streaming response display, prompt input, loading states."
    if "file_upload" in flags:
        feature_notes += "\n- Build drag-and-drop file upload with progress bar and preview."
    if "search" in flags:
        feature_notes += "\n- Build search bar with debounced input, autocomplete dropdown, and results page."
    if "social" in flags:
        feature_notes += "\n- Build user profile pages, activity feed, comment threads, and follow/unfollow."
    if "analytics" in flags:
        feature_notes += "\n- Build dashboard page with Recharts: line charts, bar charts, stat cards."
    if "scheduling" in flags:
        feature_notes += "\n- Build calendar view, booking form, and availability picker."

    dir_structure = _domain_dir_frontend(domain)
    pages_section = _domain_pages_block(domain)
    workflows_section = _domain_workflows_block(domain)

    if not pages_section:
        pages_section = """
## Pages to Build (based on the idea)
Analyse the idea and build pages for every core workflow."""

    pages_section += """
Each page must include:
- Proper loading states (skeleton UI)
- Error states with retry option
- Empty states with call-to-action
- Responsive layout (mobile-first)
- Proper SEO: page title, meta description"""

    return f"""You are a senior frontend engineer specialising in Next.js and React.
Produce **COMPLETE, WORKING, PRODUCTION-READY** frontend code for the application below.

## Application Idea
{idea}
{f"{chr(10)}Target Users: {target_users}" if target_users else ""}

## Tech Stack (use these exact technologies)
{_stack_block(stack, ["frontend", "frontend_ui"])}
- Forms: react-hook-form + zod validation
- HTTP client: fetch API with a typed wrapper (no axios)
- State: React Context for auth state; component-local state for everything else (or Zustand if complex)

## Directory Structure (create ALL files)
{dir_structure}
{pages_section}
{workflows_section if workflows_section else ""}
{feature_notes}

## API Integration
- Central ``api-client.js`` that:
  - Adds Authorization Bearer header from stored token
  - Handles 401 by attempting token refresh, then redirect to login
  - Returns typed response objects
  - Throws descriptive errors for non-2xx responses
- Every API call uses this client — no raw fetch() anywhere else.

## Authentication Flow
- Login page → POST /api/auth/login → store tokens → redirect to dashboard
- Register page → POST /api/auth/register → auto-login → redirect to dashboard
- AuthProvider wraps the dashboard layout; redirects unauthenticated users to login
- Logout clears tokens and redirects to landing page

## Forms
- Use react-hook-form for every form
- Define zod schemas matching backend Pydantic schemas
- Show field-level validation errors
- Disable submit button while loading
- Show toast/notification on success or error
{_QUALITY_FOOTER}"""


def _database_schema(idea: str, flags: Set[str], stack: StackChoice, domain: Optional[Dict] = None) -> str:
    extra = ""
    if "multi_tenancy" in flags:
        extra += "\n- Add ``tenant_id`` (FK) to every tenant-scoped table and Row-Level Security policies."
    if "ai" in flags:
        extra += "\n- Include a ``vector`` column (pgvector) for embedding storage where relevant."
    if "scheduling" in flags:
        extra += "\n- Include ``tstzrange`` columns for availability windows with exclusion constraints."
    if "analytics" in flags:
        extra += "\n- Include a hypertable or partitioned events table for time-series analytics data."

    entities_section = _domain_entities_block(domain)
    if entities_section:
        entity_design = f"""{entities_section}

1. **Entity Design** — Create tables for ALL the entities listed above. For each:
   - Table name (snake_case, plural)
   - ALL columns listed above PLUS any additional columns you identify, with: name, type (PostgreSQL types), nullable, default, constraints
   - Primary key: UUID v4 (``gen_random_uuid()``)
   - Timestamps: ``created_at TIMESTAMPTZ DEFAULT now()``, ``updated_at TIMESTAMPTZ``"""
    else:
        entity_design = """
1. **Entity Design** — Identify every entity from the idea. For each entity provide:
   - Table name (snake_case, plural)
   - ALL columns with: name, type (use PostgreSQL types), nullable, default, constraints
   - Primary key: UUID v4 (``gen_random_uuid()``)
   - Timestamps: ``created_at TIMESTAMPTZ DEFAULT now()``, ``updated_at TIMESTAMPTZ``"""

    return f"""You are a senior database architect specialising in PostgreSQL.
Produce a **COMPLETE, MIGRATION-READY** database schema for the application below.

## Application Idea
{idea}

## Tech Stack
{_stack_block(stack, ["database"])}

## Requirements
{entity_design}

2. **Relationships** — For every FK:
   - Column name, referenced table, ON DELETE behaviour (CASCADE / SET NULL / RESTRICT)
   - For many-to-many: create explicit join tables

3. **Indexes** — For each index:
   - Columns, type (btree / gin / gist), unique or not
   - Comment explaining which query it optimises

4. **Constraints** — CHECK constraints, UNIQUE constraints, NOT NULL where appropriate

5. **Alembic Migration** — Produce a complete initial Alembic migration file (``alembic/versions/001_initial.py``)
   using ``op.create_table``, ``op.create_index``, ``op.create_foreign_key``.

6. **Seed Data** — A Python seed script (``backend/scripts/seed.py``) that inserts realistic sample data
   for development (at least 5 rows per table).
{extra}
{_QUALITY_FOOTER}"""


def _auth_setup(idea: str, flags: Set[str], stack: StackChoice, domain: Optional[Dict] = None) -> str:
    extra = ""
    if "auth_advanced" in flags:
        extra += """
- Implement Role-Based Access Control (RBAC):
  - Define roles: superadmin, admin, member, viewer
  - Create a ``roles`` table and ``user_roles`` join table
  - ``require_role("admin")`` dependency for protected endpoints
- Implement OAuth2 social login (Google + GitHub) via Auth.js providers
- Implement 2FA/MFA with TOTP (pyotp library): setup, verify, recovery codes
"""
    if "multi_tenancy" in flags:
        extra += """
- Implement tenant-scoped auth: users belong to organizations, JWT includes ``org_id``
- Implement invite flow: admin invites user by email → user registers → auto-joins org
"""

    return f"""You are a senior security engineer specialising in authentication and authorization.
Produce **COMPLETE, PRODUCTION-READY** authentication and authorization code.

## Application Idea
{idea}

## Tech Stack
{_stack_block(stack, ["auth", "backend", "frontend", "database"])}

## Backend Auth (FastAPI)

1. **Password Hashing** — bcrypt via passlib CryptContext
2. **JWT Tokens** — Access token (15 min) + Refresh token (7 days)
   - Payload: ``{{"sub": user_id, "role": role, "exp": ..., "iat": ...}}``
   - Sign with HS256 using a secret from env var ``JWT_SECRET``
3. **Auth Endpoints**:
   - ``POST /api/auth/register`` — Create user, hash password, return tokens
   - ``POST /api/auth/login`` — Verify credentials, return tokens
   - ``POST /api/auth/refresh`` — Accept refresh token, return new access token
   - ``POST /api/auth/logout`` — Blacklist refresh token (store in Redis or DB)
   - ``POST /api/auth/forgot-password`` — Send reset email with time-limited token
   - ``POST /api/auth/reset-password`` — Verify token, update password
4. **Dependencies**:
   - ``get_current_user`` — Extracts and validates JWT from Authorization header
   - ``require_authenticated`` — Raises 401 if no valid user
{extra}

## Frontend Auth (Next.js)
1. **AuthContext** — React Context + Provider with: user, login(), register(), logout(), isLoading
2. **Token Storage** — Store access token in memory, refresh token in httpOnly cookie
3. **Auth Guard** — Wrapper component / middleware that redirects to /login if unauthenticated
4. **Pages**: Login, Register, Forgot Password, Reset Password (with token from email link)
{_QUALITY_FOOTER}"""


def _api_documentation(idea: str, flags: Set[str], stack: StackChoice, domain: Optional[Dict] = None) -> str:
    endpoints_ref = _domain_endpoints_block(domain)
    entities_ref = _domain_entities_block(domain)

    return f"""You are a senior API designer. Produce a **COMPLETE OpenAPI 3.0 specification** (YAML)
for the application below, plus a human-readable API reference document in Markdown.

## Application Idea
{idea}

## Tech Stack
{_stack_block(stack, ["backend", "auth"])}
{entities_ref}
{endpoints_ref}

## Requirements

1. **Every Endpoint** — Document every endpoint listed above (and standard auth endpoints). For each:
   - HTTP method + path (e.g., ``GET /api/users/{{id}}``)
   - Summary and description
   - Path parameters, query parameters
   - Request body schema with example JSON
   - Success response schema with example JSON
   - Error responses: 400, 401, 403, 404, 409, 422, 500 (only applicable ones)
   - Auth requirement: public, authenticated, or specific role

2. **Schemas** — Define reusable component schemas for every domain entity (create, read, update, list).

3. **Authentication** — Document the Bearer token scheme and how to obtain tokens.

4. **Pagination** — Document the standard pagination query params and response envelope.

5. **Rate Limiting** — Document rate limit headers (X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset).

6. **Versioning** — API is versioned via URL prefix ``/api/v1/``.

Produce two outputs:
- ``openapi.yaml`` — Full OpenAPI 3.0 spec
- ``API_REFERENCE.md`` — Human-readable endpoint reference
{_QUALITY_FOOTER}"""


def _deployment_config(idea: str, flags: Set[str], stack: StackChoice, domain: Optional[Dict] = None) -> str:
    extra = ""
    if "realtime" in flags:
        extra += "\n- Configure sticky sessions or WebSocket-compatible load balancer."
    if "search" in flags:
        extra += f"\n- Include {stack.search} service in docker-compose."
    if "cache" != "None":
        extra += "\n- Include Redis service in docker-compose with persistence."

    return f"""You are a senior DevOps engineer. Produce **COMPLETE, PRODUCTION-READY** deployment
and infrastructure configuration for the application below.

## Application Idea
{idea}

## Tech Stack
{_stack_block(stack, ["backend", "frontend", "database", "cache", "infra", "monitoring"])}

## Deliverables (create ALL files)

### 1. Dockerfiles
- ``backend/Dockerfile`` — Multi-stage: builder (install deps) → runner (slim image, non-root user)
- ``frontend/Dockerfile`` — Multi-stage: builder (npm build) → runner (Next.js standalone output)

### 2. Docker Compose (local development)
```yaml
# docker-compose.yml
services:
  backend:    # FastAPI on port 8000, hot-reload, .env file
  frontend:   # Next.js on port 3000, hot-reload
  db:         # PostgreSQL 16 with named volume
  redis:      # Redis 7 (if caching/realtime needed)
  # Additional services based on stack
```

### 3. CI/CD Pipeline (GitHub Actions)
```.github/workflows/ci.yml```
- **Lint**: ruff (Python) + eslint (JS)
- **Test**: pytest with PostgreSQL service container; jest for frontend
- **Build**: Docker build for both services
- **Deploy**: Push to container registry → deploy to {stack.infra.split('(')[0].strip() if '(' in stack.infra else stack.infra}
- Trigger: push to main, PR checks

### 4. Environment Configuration
- ``.env.example`` for backend with every variable documented
- ``.env.local.example`` for frontend with NEXT_PUBLIC_ variables
- Document which secrets must be set in CI/CD

### 5. Database Migrations in Deploy
- Run ``alembic upgrade head`` as a pre-deploy step
- Include a health check that verifies DB connectivity
{extra}
{_QUALITY_FOOTER}"""


def _testing_suite(idea: str, flags: Set[str], stack: StackChoice, domain: Optional[Dict] = None) -> str:
    extra = ""
    if "payments" in flags:
        extra += "\n- Mock Stripe API calls using stripe-mock or pytest fixtures."
    if "ai" in flags:
        extra += "\n- Mock OpenAI API responses with deterministic fixtures."
    if "realtime" in flags:
        extra += "\n- Test WebSocket connections using httpx AsyncClient WebSocket support."

    # Build specific test file list from domain entities
    test_files = "- ``test_auth.py`` — Register, login, refresh, logout, invalid credentials, expired tokens\n"
    if domain and "entities" in domain:
        for ent in domain["entities"]:
            tname = ent.get("table_name", ent["name"].lower() + "s")
            test_files += (f"- ``test_{tname}.py`` — {ent['name']} CRUD operations, validation errors, "
                           f"auth requirements, pagination, edge cases\n")
    else:
        test_files += ("- ``test_[domain].py`` — For each domain entity: CRUD operations, validation errors,\n"
                       "  auth requirements, pagination, edge cases\n")
    test_files += "- ``test_middleware.py`` — Error handler, rate limiting"

    return f"""You are a senior QA engineer. Produce a **COMPLETE, READY-TO-RUN** test suite
for the application below.

## Application Idea
{idea}

## Tech Stack
{_stack_block(stack, ["backend", "frontend", "testing", "database"])}

## Backend Tests (pytest)

### Setup
- ``backend/tests/conftest.py``:
  - Create async test database (SQLite in-memory or test PostgreSQL)
  - ``async_client`` fixture using httpx AsyncClient with app
  - ``db_session`` fixture with transaction rollback
  - ``authenticated_client`` fixture (pre-logged-in user)
  - Factory fixtures for creating test entities

### Test Files (create ALL)
{test_files}

### Coverage
- Target: 80%+ line coverage
- Config in ``pyproject.toml``: ``[tool.pytest.ini_options]`` and ``[tool.coverage.run]``

## Frontend Tests (Jest + React Testing Library)

### Setup
- ``frontend/jest.config.js`` with Next.js preset
- ``frontend/__tests__/setup.js`` with global mocks

### Test Files
- Test each page component: renders correctly, handles loading, handles errors
- Test form components: validation, submission, error display
- Test API client: auth header injection, error handling, token refresh

## E2E Tests (Playwright)

### Setup
- ``playwright.config.js`` with base URL, browser config, CI settings

### Test Files
- ``e2e/auth.spec.js`` — Full registration → login → dashboard flow
- ``e2e/[core_feature].spec.js`` — Happy-path workflow for each major feature
{extra}
{_QUALITY_FOOTER}"""


def _security_checklist(idea: str, flags: Set[str], stack: StackChoice, industry: Optional[str], domain: Optional[Dict] = None) -> str:
    compliance = ""
    if industry:
        industry_lower = industry.lower()
        if any(k in industry_lower for k in ["health", "medical", "hipaa"]):
            compliance += "\n- **HIPAA**: PHI encryption at rest and in transit, audit logging, BAA with cloud provider, minimum necessary access."
        if any(k in industry_lower for k in ["finance", "fintech", "banking", "pci"]):
            compliance += "\n- **PCI-DSS**: Tokenize card data (never store raw), use Stripe for payment handling, quarterly vulnerability scans."
        if any(k in industry_lower for k in ["eu", "gdpr", "europe"]):
            compliance += "\n- **GDPR**: Cookie consent, data export endpoint, right-to-deletion endpoint, DPA with processors."
    if not compliance:
        compliance = "\n- **GDPR basics**: Cookie consent banner, privacy policy page, data deletion capability."

    return f"""You are a senior application security engineer. Produce a **COMPLETE security
hardening guide and implementation checklist** for the application below.

## Application Idea
{idea}

## Tech Stack
{_stack_block(stack, ["backend", "frontend", "auth", "database", "infra"])}

## Security Checklist (implement or verify ALL)

### Input Validation & Sanitization
- Validate ALL user input with Pydantic schemas (backend) and zod (frontend)
- Sanitize HTML output to prevent XSS (use DOMPurify on frontend if rendering user HTML)
- Validate file uploads: type whitelist, size limit, magic byte checking

### Authentication Security
- Hash passwords with bcrypt (cost factor 12)
- JWT signed with strong secret (256-bit minimum), short-lived access tokens (15 min)
- Refresh token rotation: invalidate old refresh token on use
- Account lockout after 5 failed login attempts (progressive delay)
- Secure token storage: httpOnly cookies for refresh token

### HTTP Security Headers
- Content-Security-Policy (CSP): strict, no inline scripts
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- Strict-Transport-Security: max-age=31536000; includeSubDomains
- Referrer-Policy: strict-origin-when-cross-origin
- Permissions-Policy: restrict camera, microphone, geolocation

### API Security
- Rate limiting: 100 requests/min for authenticated, 20/min for unauthenticated
- CORS: allow only known origins (not ``*`` in production)
- Request size limits (1 MB default, larger for file uploads)
- No sensitive data in URLs or logs

### Database Security
- Parameterised queries only (SQLAlchemy ORM handles this)
- Least-privilege database user (no SUPERUSER)
- Encrypt sensitive columns (email, PII) at rest if required
- Regular backups with tested restore procedure

### Dependency Security
- ``pip-audit`` in CI for Python dependencies
- ``npm audit`` in CI for Node dependencies
- Dependabot or Renovate for automated update PRs

### Secrets Management
- All secrets in environment variables, never in code
- ``.env`` in ``.gitignore``
- Rotate secrets quarterly; document rotation procedure

### Compliance
{compliance}

### Monitoring & Incident Response
- Log all authentication events (login, failed login, password reset)
- Alert on anomalous patterns (spike in 401s, unusual geolocations)
- Document incident response runbook: detection → containment → recovery → postmortem
{_QUALITY_FOOTER}"""


# ===================================================================
# CONDITIONAL PROMPTS (only when feature flag is detected)
# ===================================================================

def _realtime_implementation(idea: str, stack: StackChoice, domain: Optional[Dict] = None) -> str:
    return f"""You are a senior backend engineer specialising in real-time systems.
Produce **COMPLETE, PRODUCTION-READY** real-time communication code.

## Application Idea
{idea}

## Tech Stack
{_stack_block(stack, ["backend", "cache", "frontend"])}

## Backend (FastAPI WebSockets)

1. **WebSocket Manager** (``app/services/ws_manager.py``):
   - Connection registry: map of user_id → set of WebSocket connections
   - ``connect(ws, user_id)``, ``disconnect(ws, user_id)``, ``broadcast(room, event, data)``
   - Redis pub/sub for multi-process broadcast (if running multiple workers)

2. **WebSocket Endpoint** (``app/api/routes/ws.py``):
   - ``/ws?token=<jwt>`` — authenticate via query param JWT
   - Parse incoming messages as JSON: ``{{"type": "...", "payload": {{...}}}}``
   - Route to appropriate handler based on ``type``
   - Send outgoing messages as JSON: ``{{"type": "...", "payload": {{...}}, "timestamp": "..."}}``

3. **Event Types** (derive from the idea):
   - Define specific event types for the application's real-time features
   - Include presence events: ``user_joined``, ``user_left``, ``typing``
   - Include data events specific to the domain

4. **Redis Pub/Sub** (``app/services/pubsub.py``):
   - Subscribe to channels on worker startup
   - Publish events when data changes (after DB write)
   - Handle reconnection to Redis

## Frontend (React)

1. **useWebSocket hook** (``lib/use-websocket.js``):
   - Connect with JWT token
   - Auto-reconnect with exponential backoff (1s, 2s, 4s, 8s, max 30s)
   - Parse incoming JSON messages
   - Expose: ``sendMessage(type, payload)``, ``lastMessage``, ``isConnected``
   - Clean up on unmount

2. **Real-time UI components**:
   - Connection status indicator (green/yellow/red dot)
   - Live data updates without page refresh
   - Optimistic UI updates with rollback on failure
{_QUALITY_FOOTER}"""


def _payment_integration(idea: str, stack: StackChoice, domain: Optional[Dict] = None) -> str:
    return f"""You are a senior backend engineer specialising in payment systems.
Produce **COMPLETE, PRODUCTION-READY** Stripe payment integration code.

## Application Idea
{idea}

## Tech Stack
{_stack_block(stack, ["backend", "frontend", "auth", "database"])}
- Payments: Stripe Python SDK (stripe) + Stripe.js + @stripe/react-stripe-js

## Backend

1. **Stripe Service** (``app/services/stripe_service.py``):
   - ``create_customer(user)`` — Create Stripe customer on registration
   - ``create_checkout_session(user, price_id)`` — Create Checkout Session
   - ``create_billing_portal_session(user)`` — Customer self-service
   - ``handle_webhook(payload, sig_header)`` — Verify and process webhook events

2. **Webhook Handler** (``app/api/routes/webhooks.py``):
   - ``POST /api/webhooks/stripe`` — Raw body, verify signature
   - Handle events: ``checkout.session.completed``, ``customer.subscription.created``,
     ``customer.subscription.updated``, ``customer.subscription.deleted``,
     ``invoice.payment_succeeded``, ``invoice.payment_failed``
   - Update local subscription status in database
   - Idempotency: store processed event IDs to prevent duplicate processing

3. **Database Models**:
   - ``Subscription``: id, user_id, stripe_subscription_id, stripe_customer_id, status, plan, current_period_end
   - ``PaymentEvent``: id, stripe_event_id, type, processed_at (for idempotency)

4. **Pricing Endpoints**:
   - ``GET /api/pricing`` — Return available plans and prices
   - ``POST /api/checkout`` — Create checkout session, return URL
   - ``POST /api/billing-portal`` — Create portal session, return URL
   - ``GET /api/subscription`` — Current user's subscription status

## Frontend

1. **Pricing Page** (``app/(marketing)/pricing/page.js``):
   - Display plan cards with features, price, CTA button
   - Highlight recommended plan
   - FAQ section

2. **Checkout Flow**:
   - CTA button → call backend → redirect to Stripe Checkout
   - Success page with confetti / confirmation
   - Cancel page with "try again" option

3. **Subscription Management** (``app/(dashboard)/settings/billing/page.js``):
   - Show current plan, next billing date, payment method
   - "Manage Subscription" button → Stripe Customer Portal
   - Handle plan changes and cancellations
{_QUALITY_FOOTER}"""


def _ai_integration(idea: str, stack: StackChoice, domain: Optional[Dict] = None) -> str:
    return f"""You are a senior AI/ML engineer specialising in LLM integration.
Produce **COMPLETE, PRODUCTION-READY** AI integration code.

## Application Idea
{idea}

## Tech Stack
{_stack_block(stack, ["backend", "ai", "database", "cache"])}

## Backend

1. **LLM Service** (``app/services/llm_service.py``):
   - ``generate(system_prompt, user_prompt, max_tokens, temperature)`` → str
   - ``generate_stream(system_prompt, user_prompt)`` → AsyncGenerator[str]
   - ``embed(text)`` → List[float] (for embeddings)
   - Retry with exponential backoff on rate limits (429)
   - Token counting before requests to stay within limits
   - Cost tracking: log model, tokens_in, tokens_out per request

2. **Prompt Manager** (``app/services/prompt_manager.py``):
   - Store prompt templates with versioning
   - Variable interpolation: ``{{user_name}}``, ``{{context}}``
   - A/B test different prompt versions (optional)

3. **RAG Pipeline** (if relevant to the idea) (``app/services/rag.py``):
   - ``index_document(doc_id, text)`` — Chunk text, generate embeddings, store in pgvector
   - ``query(question, top_k=5)`` → List of relevant chunks
   - Chunking strategy: 500 tokens with 50-token overlap
   - Similarity search: cosine distance via pgvector ``<=>`` operator

4. **Streaming Endpoint** (``app/api/routes/ai.py``):
   - ``POST /api/ai/generate`` — Return full response
   - ``POST /api/ai/stream`` — Return Server-Sent Events (SSE) stream
   - Rate limit: 10 AI requests per minute per user

## Frontend

1. **AI Chat / Interaction Component**:
   - Streaming text display (character by character or chunk by chunk)
   - Loading indicator while waiting for first token
   - Stop generation button
   - Copy response button
   - Markdown rendering for AI responses

2. **SSE Client** (``lib/sse-client.js``):
   - Connect to SSE endpoint with auth header
   - Parse incoming events
   - Handle connection errors and retries
{_QUALITY_FOOTER}"""


def _mobile_api(idea: str, stack: StackChoice, domain: Optional[Dict] = None) -> str:
    return f"""You are a senior mobile API architect. Produce a **COMPLETE design and implementation**
for a mobile-optimized API layer.

## Application Idea
{idea}

## Tech Stack
{_stack_block(stack, ["backend", "frontend", "auth"])}

## Requirements

1. **API Design for Mobile**:
   - Composite endpoints that reduce round-trips (e.g., ``/api/mobile/home`` returns user + recent items + notifications in one call)
   - Sparse fieldsets: ``?fields=id,name,avatar`` to reduce payload size
   - Efficient pagination with cursor-based pagination (not page numbers)
   - ETag / If-None-Match for conditional requests
   - Compressed responses (gzip)

2. **Push Notifications** (``app/services/push_service.py``):
   - FCM (Firebase Cloud Messaging) for Android + iOS
   - ``register_device(user_id, device_token, platform)``
   - ``send_push(user_id, title, body, data)``
   - Store device tokens in database (``DeviceToken`` model)
   - Batch sending for bulk notifications

3. **Offline-First Patterns**:
   - API responses include ``updated_at`` timestamps for sync
   - ``GET /api/sync?since=<timestamp>`` endpoint returns changed records
   - Conflict resolution: last-write-wins with server timestamp

4. **Mobile Auth**:
   - Biometric auth support (device-side, API provides long-lived refresh token)
   - Token refresh without user interaction
   - Device fingerprinting for security alerts
{_QUALITY_FOOTER}"""


def _search_implementation(idea: str, stack: StackChoice, domain: Optional[Dict] = None) -> str:
    return f"""You are a senior search engineer. Produce **COMPLETE, PRODUCTION-READY** search implementation.

## Application Idea
{idea}

## Tech Stack
{_stack_block(stack, ["backend", "search", "database"])}

## Requirements

1. **Search Engine Setup** (``app/services/search_service.py``):
   - Initialize search client (Meilisearch / Elasticsearch)
   - Define indexes for each searchable entity
   - Configure searchable fields, filterable fields, sortable fields
   - Configure ranking rules and relevance tuning

2. **Indexing Pipeline**:
   - Index new records on creation (async task or post-commit hook)
   - Update index on record update
   - Remove from index on deletion
   - Bulk re-index command for initial setup / recovery

3. **Search API** (``app/api/routes/search.py``):
   - ``GET /api/search?q=<query>&type=<entity>&filters=<json>&sort=<field>&page=<n>``
   - Response: ``{{"hits": [...], "total": N, "query": "...", "facets": {{...}}}}``
   - Faceted search: return counts per category/tag
   - Highlight matching terms in results

4. **Frontend Search UI**:
   - Search bar with debounced input (300ms)
   - Autocomplete dropdown showing top 5 suggestions
   - Results page with facet sidebar and result cards
   - "No results" state with suggestions
   - Search analytics: track popular queries
{_QUALITY_FOOTER}"""


def _file_upload_system(idea: str, stack: StackChoice, domain: Optional[Dict] = None) -> str:
    return f"""You are a senior backend engineer specialising in file handling and cloud storage.
Produce **COMPLETE, PRODUCTION-READY** file upload system.

## Application Idea
{idea}

## Tech Stack
{_stack_block(stack, ["backend", "file_storage", "database"])}

## Requirements

1. **Upload Service** (``app/services/upload_service.py``):
   - ``generate_presigned_url(filename, content_type, max_size_mb)`` → presigned PUT URL + file key
   - ``confirm_upload(file_key, user_id)`` → create DB record after client confirms upload
   - ``delete_file(file_key)`` → remove from S3/R2 + DB record
   - File type whitelist: images (jpg, png, webp, gif), documents (pdf, docx), video (mp4, webm)
   - Max file size: 10 MB for images, 50 MB for documents, 500 MB for video

2. **Image Processing** (``app/services/image_processor.py``):
   - Generate thumbnails: 150x150 (avatar), 400x400 (preview), 1200x1200 (full)
   - Convert to WebP for web delivery
   - Strip EXIF metadata for privacy
   - Use Pillow or Sharp (via subprocess)

3. **Database Models**:
   - ``Upload``: id, user_id, file_key, original_name, content_type, size_bytes, status (pending/confirmed/deleted), created_at
   - Polymorphic association: uploads can be attached to any entity via ``entity_type`` + ``entity_id``

4. **API Endpoints**:
   - ``POST /api/uploads/presign`` → {{"upload_url": "...", "file_key": "..."}}
   - ``POST /api/uploads/confirm`` → {{"id": "...", "url": "..."}}
   - ``DELETE /api/uploads/{{id}}``
   - ``GET /api/uploads?entity_type=...&entity_id=...`` → list uploads for an entity

5. **Frontend Upload Component** (``components/ui/FileUpload.js``):
   - Drag-and-drop zone with click-to-browse fallback
   - File type and size validation (client-side, before upload)
   - Upload progress bar (using XMLHttpRequest or fetch with ReadableStream)
   - Preview: image thumbnail, document icon, video player
   - Multi-file upload support
   - Remove / replace uploaded file
{_QUALITY_FOOTER}"""


# ===================================================================
# MVP PROMPTS (lean, 3 essentials only)
# ===================================================================

_MVP_QUALITY = """
## Quality Requirements
- All code must be COMPLETE — no TODOs, no placeholders.
- Include basic error handling for critical operations.
- Keep it simple — this is an MVP, not production code.

## Output Format
Produce the code as a series of complete files. Precede each file with:
```
# filepath: path/to/file.py
```
"""


def _mvp_backend(idea: str, target_users: Optional[str], stack: StackChoice, domain: Optional[Dict] = None) -> str:
    entities_section = _domain_entities_block(domain)
    endpoints_section = _domain_endpoints_block(domain)

    if not endpoints_section:
        endpoints_section = """## Endpoints
Derive REST endpoints from the idea. At minimum:
- POST /auth/register, POST /auth/login
- CRUD for each core entity (GET list, GET by id, POST, PUT, DELETE)
- GET /health"""

    return f"""You are a backend engineer. Build a **minimal working backend** (MVP) as fast as possible.

## Idea
{idea}
{f"{chr(10)}Target Users: {target_users}" if target_users else ""}

## Tech Stack
{_stack_block(stack, ["backend", "database", "auth"])}
{entities_section}

## Keep It Simple
- Flat structure: ``app/main.py``, ``app/models.py``, ``app/routes.py``, ``app/schemas.py``, ``app/database.py``, ``app/auth.py``
- NO separate service layer, NO middleware folder, NO rate limiting
- SQLAlchemy models with basic relationships
- Pydantic schemas for request/response
- JWT auth: register + login endpoints only (no refresh, no password reset)
- CRUD routes for each core entity listed above
- Simple error handling (HTTPException)
- Include ``requirements.txt`` and ``.env.example``

## Database
- PostgreSQL with SQLAlchemy (sync is fine for MVP)
- Every model: id (UUID), created_at. Add domain fields as needed.
- One Alembic initial migration

{endpoints_section}
{_MVP_QUALITY}"""


def _mvp_frontend(idea: str, target_users: Optional[str], stack: StackChoice, domain: Optional[Dict] = None) -> str:
    pages_section = _domain_pages_block(domain)

    if not pages_section:
        pages_section = """## Pages
- Landing, Login, Register, Dashboard (main feature), Settings"""

    return f"""You are a frontend engineer. Build a **minimal working frontend** (MVP) as fast as possible.

## Idea
{idea}
{f"{chr(10)}Target Users: {target_users}" if target_users else ""}

## Tech Stack
{_stack_block(stack, ["frontend", "frontend_ui"])}

## Keep It Simple
- Use Next.js App Router with minimal pages
- Use simple ``fetch()`` wrapper for API calls — no complex state management
- Store JWT token in localStorage (fine for MVP)
- Basic responsive layout with Tailwind
- Loading spinners, not skeleton UIs
- Simple form handling (controlled inputs, basic validation)

{pages_section}

## Structure
```
app/
  page.js              # Landing page
  login/page.js        # Login form
  register/page.js     # Register form
  dashboard/page.js    # Main feature page
  dashboard/layout.js  # Nav sidebar
lib/
  api.js               # fetch wrapper with auth header
```

## Must Have
- Auth flow: register → login → redirect to dashboard
- Dashboard shows the core feature of the app
- Logout button
- Mobile-friendly layout
{_MVP_QUALITY}"""


def _mvp_database(idea: str, stack: StackChoice, domain: Optional[Dict] = None) -> str:
    entities_section = _domain_entities_block(domain)

    return f"""You are a database engineer. Design a **minimal database schema** for an MVP.

## Idea
{idea}

## Tech Stack
{_stack_block(stack, ["database"])}
{entities_section}

## Keep It Simple
- Only the tables absolutely needed for the core feature
- Users table: id (UUID), email, password_hash, name, created_at
- Domain tables for each entity listed above (include all specified fields)
- Simple foreign keys (ON DELETE CASCADE)
- Basic indexes on email and foreign keys only
- ONE Alembic migration file that creates everything

## Deliverables
1. SQLAlchemy models in ``app/models.py``
2. Alembic migration: ``alembic/versions/001_initial.py``
3. Brief seed script: ``scripts/seed.py`` (3 rows per table)
{_MVP_QUALITY}"""


# ===================================================================
# MASTER PROMPTS — single "build it all" prompt
# ===================================================================

def _master_prompt_production(
    idea: str,
    target_users: Optional[str],
    flags: Set[str],
    stack: StackChoice,
    industry: Optional[str],
    domain: Optional[Dict] = None,
) -> str:
    """Generate a single comprehensive prompt to build the entire production app."""
    entities_section = _domain_entities_block(domain)
    endpoints_section = _domain_endpoints_block(domain)
    pages_section = _domain_pages_block(domain)
    workflows_section = _domain_workflows_block(domain)

    # Feature integrations
    feature_sections = ""
    if "realtime" in flags:
        feature_sections += """
### Real-Time Features
- Implement WebSocket endpoint at ``/ws?token=<jwt>`` using FastAPI WebSocket support
- Build WebSocket connection manager with room-based broadcasting
- Use Redis pub/sub for multi-worker message distribution
- Frontend: ``useWebSocket`` hook with auto-reconnect (exponential backoff)
- Show connection status indicator in the UI
"""
    if "payments" in flags:
        feature_sections += """
### Payment Integration (Stripe)
- Create Stripe customers on user registration
- Implement checkout session creation and billing portal
- Handle webhooks: ``checkout.session.completed``, ``customer.subscription.created/updated/deleted``
- Build pricing page with plan cards and checkout flow
- Build subscription management in user settings
- Store subscription status in database with Stripe IDs
"""
    if "ai" in flags:
        feature_sections += """
### AI / LLM Integration
- Build LLM service with streaming support (``generate`` + ``generate_stream``)
- Implement SSE endpoint for real-time AI responses
- Build prompt management with versioning
- Frontend: streaming text display with stop button and markdown rendering
- Rate limit AI requests (10/min per user)
- Track token usage and costs
"""
    if "file_upload" in flags:
        feature_sections += """
### File Upload System
- Implement presigned URL upload flow to S3/R2
- Generate thumbnails and WebP conversions for images
- File type whitelist + size limits (10MB images, 50MB docs)
- Frontend: drag-and-drop upload with progress bar and preview
"""
    if "search" in flags:
        feature_sections += f"""
### Search
- Set up {stack.search} with indexes for each searchable entity
- Implement search indexing pipeline (index on create/update, remove on delete)
- Build search API with faceted filtering and result highlighting
- Frontend: debounced search bar with autocomplete dropdown
"""
    if "scheduling" in flags:
        feature_sections += """
### Scheduling
- Implement availability windows with conflict detection
- Build booking flow with confirmation and reminders
- Frontend: calendar view and availability picker
"""
    if "notifications" in flags:
        feature_sections += """
### Notifications
- Build notification service: in-app, email (via Resend)
- Store notification preferences per user
- Implement real-time notification delivery
"""
    if "multi_tenancy" in flags:
        feature_sections += """
### Multi-Tenancy
- Organization model with tenant-scoped queries
- Middleware to inject current tenant from JWT
- Invite flow: admin invites by email → user joins org
- Role-based access within organizations
"""
    if "analytics" in flags:
        feature_sections += """
### Analytics Dashboard
- Build aggregation queries for key metrics
- Frontend: Recharts dashboard with line/bar charts, stat cards, date filtering
"""
    if "social" in flags:
        feature_sections += """
### Social Features
- User profiles with avatar and bio
- Activity feed with pagination
- Comment threads with nested replies
- Follow/unfollow system
"""

    dir_backend = _domain_dir_backend(domain)
    dir_frontend = _domain_dir_frontend(domain)

    return f"""You are a senior full-stack engineer with 15+ years of experience.
Build the **COMPLETE, PRODUCTION-READY** application described below.
Generate ALL code files — backend, frontend, database, auth, deployment — in a single response.
Do NOT leave any placeholders, TODOs, or "implement here" comments.

## Project Description
{idea}
{f"{chr(10)}**Target Users:** {target_users}" if target_users else ""}
{f"{chr(10)}**Industry:** {industry}" if industry else ""}

## Tech Stack (use these exact technologies)
{_stack_block(stack)}
{entities_section}
{endpoints_section}
{pages_section}
{workflows_section}

## Backend Structure
{dir_backend}

## Frontend Structure
{dir_frontend}

## Database Schema
- Use PostgreSQL with SQLAlchemy 2.0 async (``mapped_column``)
- Every model: ``id`` (UUID PK), ``created_at``, ``updated_at``
- Define all foreign keys with ON DELETE behaviour
- Add indexes on columns used in WHERE/ORDER BY
- Produce a complete Alembic initial migration
- Include a seed script with realistic sample data (5+ rows per table)

## Authentication & Authorization
- JWT access token (15 min) + refresh token (7 days), signed with HS256
- Password hashing with bcrypt via passlib
- Endpoints: register, login, refresh, logout, forgot-password, reset-password
- ``get_current_user`` dependency for protected routes
- Frontend: AuthContext with login/register/logout, token stored in memory + httpOnly cookie for refresh
- Auth guard redirecting unauthenticated users to login

## API Design
- RESTful JSON API at ``/api/`` prefix
- Standard pagination: ``?page=1&per_page=20`` → ``{{"items": [...], "total": N, "page": N, "per_page": N, "pages": N}}``
- Error responses: ``{{"detail": "...", "code": "..."}}``
- Rate limiting: 100 req/min authenticated, 20 req/min unauthenticated
- CORS configured for frontend origin

## Frontend Requirements
- react-hook-form + zod for every form
- Central API client with auth header injection, 401 handling, and token refresh
- Loading states (skeleton UI), error states (with retry), empty states
- Responsive (mobile-first), SEO (page titles, meta descriptions)
- Toast notifications for success/error feedback
{f"## Feature Integrations{feature_sections}" if feature_sections else ""}

## Deployment
- ``backend/Dockerfile`` — multi-stage (builder → slim runner, non-root user)
- ``frontend/Dockerfile`` — multi-stage (npm build → Next.js standalone)
- ``docker-compose.yml`` — backend, frontend, PostgreSQL, Redis (if needed)
- ``.github/workflows/ci.yml`` — lint, test, build, deploy
- ``.env.example`` files for both services with all variables documented

## Testing
- Backend: pytest + httpx async tests for auth + all domain entities
- Frontend: Jest + React Testing Library for components and forms
- E2E: Playwright for critical user flows

## Security
- Input validation (Pydantic + zod), XSS prevention, CSRF protection
- HTTP security headers (CSP, HSTS, X-Frame-Options, etc.)
- Rate limiting, request size limits, parameterised queries only
- Secrets in env vars, ``.env`` in ``.gitignore``
{_QUALITY_FOOTER}"""


def _master_prompt_mvp(
    idea: str,
    target_users: Optional[str],
    flags: Set[str],
    stack: StackChoice,
    domain: Optional[Dict] = None,
) -> str:
    """Generate a single lean prompt to build the entire MVP app."""
    entities_section = _domain_entities_block(domain)
    endpoints_section = _domain_endpoints_block(domain)
    pages_section = _domain_pages_block(domain)
    workflows_section = _domain_workflows_block(domain)

    return f"""You are a full-stack engineer. Build a **minimal working MVP** as fast as possible.
Generate ALL code files — backend, frontend, database — in a single response.
Keep it simple. No over-engineering. Ship fast.

## Idea
{idea}
{f"{chr(10)}**Target Users:** {target_users}" if target_users else ""}

## Tech Stack
{_stack_block(stack, ["frontend", "frontend_ui", "backend", "database", "auth"])}
{entities_section}
{endpoints_section}
{pages_section}
{workflows_section}

## Backend (flat structure)
```
backend/
  app/
    main.py        # FastAPI app with CORS
    models.py      # All SQLAlchemy models
    schemas.py     # All Pydantic schemas
    routes.py      # All API routes
    database.py    # DB engine + session
    auth.py        # JWT auth (register + login)
  alembic/
    versions/001_initial.py
  requirements.txt
  .env.example
```

- PostgreSQL + SQLAlchemy (sync OK for MVP)
- JWT auth: register + login only (no refresh, no password reset)
- CRUD routes for each entity listed above
- Simple error handling (HTTPException)
- One Alembic migration

## Frontend
```
frontend/
  app/
    page.js              # Landing page
    login/page.js
    register/page.js
    dashboard/page.js    # Main feature
    dashboard/layout.js  # Nav sidebar
  lib/
    api.js               # fetch wrapper with auth header
```

- Next.js App Router + Tailwind
- Simple fetch wrapper for API calls
- JWT stored in localStorage
- Auth flow: register → login → dashboard
- Loading spinners, basic form validation
- Mobile-friendly layout

## Database
- Users table: id (UUID), email, password_hash, name, created_at
- Domain tables for each entity listed above
- Simple foreign keys (ON DELETE CASCADE)
- Basic indexes on email and FKs

{_MVP_QUALITY}"""


# ===================================================================
# PUBLIC API
# ===================================================================

def build_prompt_pack(
    idea: str,
    flags: Set[str],
    stack: StackChoice,
    target_users: Optional[str] = None,
    constraints: Optional[List[str]] = None,
    industry: Optional[str] = None,
    mode: str = "production",
    domain: Optional[Dict] = None,
    tool=None,
) -> Dict[str, str]:
    """Build the prompt dictionary.

    If *tool* is a ToolProfile, dispatches to tool-specific prompt builders.
    Otherwise:
    - mode="mvp": master prompt + 3 lean prompts
    - mode="production": master prompt + 9 core + conditional heavy prompts
    """
    # ── Tool-specific dispatch ──
    if tool is not None:
        from app.services.tool_prompts import (
            build_lovable_prompts,
            build_replit_prompts,
            build_base44_prompts,
            build_claude_code_prompts,
        )
        slug = tool.slug
        if slug == "lovable":
            return build_lovable_prompts(idea, flags, stack, target_users, domain, mode)
        elif slug == "replit":
            return build_replit_prompts(idea, flags, stack, target_users, domain, mode)
        elif slug == "base44":
            return build_base44_prompts(idea, flags, stack, target_users, domain, mode)
        elif slug == "claude_code":
            # Claude Code uses the default prompts but with a custom master prompt
            master = build_claude_code_prompts(
                idea, flags, stack, target_users, constraints, industry, domain, mode,
            )
            prompts = _build_default_prompts(idea, flags, stack, target_users, constraints, industry, mode, domain)
            prompts["master_prompt"] = master
            return prompts

    # ── Default (no tool selected) ──
    return _build_default_prompts(idea, flags, stack, target_users, constraints, industry, mode, domain)


def _build_default_prompts(
    idea: str, flags: Set[str], stack: StackChoice,
    target_users: Optional[str], constraints: Optional[List[str]],
    industry: Optional[str], mode: str, domain: Optional[Dict],
) -> Dict[str, str]:
    """Default prompt builder (no tool selected)."""

    if mode == "mvp":
        prompts: Dict[str, str] = {}
        prompts["master_prompt"] = _master_prompt_mvp(idea, target_users, flags, stack, domain)
        prompts["backend_code"] = _mvp_backend(idea, target_users, stack, domain)
        prompts["frontend_code"] = _mvp_frontend(idea, target_users, stack, domain)
        prompts["database_schema"] = _mvp_database(idea, stack, domain)
        return prompts

    # ── Production mode ──
    prompts: Dict[str, str] = {}
    prompts["master_prompt"] = _master_prompt_production(idea, target_users, flags, stack, industry, domain)
    prompts["product_requirements"] = _product_requirements(idea, target_users, stack, domain)
    prompts["backend_code"] = _backend_code(idea, target_users, flags, stack, domain)
    prompts["frontend_code"] = _frontend_code(idea, target_users, flags, stack, domain)
    prompts["database_schema"] = _database_schema(idea, flags, stack, domain)
    prompts["auth_setup"] = _auth_setup(idea, flags, stack, domain)
    prompts["api_documentation"] = _api_documentation(idea, flags, stack, domain)
    prompts["deployment_config"] = _deployment_config(idea, flags, stack, domain)
    prompts["testing_suite"] = _testing_suite(idea, flags, stack, domain)
    prompts["security_checklist"] = _security_checklist(idea, flags, stack, industry, domain)

    if "realtime" in flags:
        prompts["realtime_implementation"] = _realtime_implementation(idea, stack, domain)
    if "payments" in flags:
        prompts["payment_integration"] = _payment_integration(idea, stack, domain)
    if "ai" in flags:
        prompts["ai_integration"] = _ai_integration(idea, stack, domain)
    if "mobile" in flags:
        prompts["mobile_api"] = _mobile_api(idea, stack, domain)
    if "search" in flags:
        prompts["search_implementation"] = _search_implementation(idea, stack, domain)
    if "file_upload" in flags:
        prompts["file_upload_system"] = _file_upload_system(idea, stack, domain)

    return prompts
