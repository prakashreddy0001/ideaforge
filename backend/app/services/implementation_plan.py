"""Granular, phased implementation plan builder."""

from typing import Dict, List, Optional, Set

from app.services.stack_selection import StackChoice


def _entity_names(domain: Optional[Dict]) -> str:
    """Return comma-separated entity names from domain, or empty string."""
    if not domain or "entities" not in domain:
        return ""
    return ", ".join(e["name"] for e in domain["entities"])


def _page_names(domain: Optional[Dict]) -> str:
    """Return comma-separated page names from domain, or empty string."""
    if not domain or "pages" not in domain:
        return ""
    return ", ".join(p["name"] for p in domain["pages"])


def _mvp_plan(stack: StackChoice, domain: Optional[Dict] = None) -> List[str]:
    """Return a short 7-step MVP plan — no phases, flat list."""
    entities = _entity_names(domain)
    models_detail = f" Models: {entities}." if entities else ""
    pages = _page_names(domain)
    pages_detail = f" Pages: {pages}." if pages else ""

    return [
        f"1. Set up monorepo with {stack.backend.split('+')[0].strip()} backend and {stack.frontend.split('+')[0].strip()} frontend.",
        f"2. Create database schema ({stack.database.split('+')[0].strip()}) and run initial Alembic migration.{models_detail}",
        f"3. Build backend: CRUD API routes, Pydantic schemas, basic JWT auth (register + login).{models_detail}",
        f"4. Build frontend: login, register, and main dashboard pages with API integration.{pages_detail}",
        "5. Add basic styling (Tailwind), responsive layout, and navigation.",
        "6. Test locally — verify end-to-end auth flow and core feature.",
        f"7. Deploy: Dockerize both services and deploy to {stack.infra.split('(')[0].strip() if '(' in stack.infra else stack.infra}.",
    ]


def build_implementation_plan(flags: Set[str], stack: StackChoice, mode: str = "production", domain: Optional[Dict] = None, tool=None) -> List[str]:
    """Return an implementation plan.

    - mode="mvp": 7 flat steps
    - mode="production": 15-25 phased steps
    - tool: optional ToolProfile for tool-specific plan adaptations
    """
    # ── Tool-specific plans ──
    if tool is not None:
        slug = tool.slug
        if slug == "lovable":
            return _lovable_plan(flags, stack, domain, mode)
        elif slug == "base44":
            return _base44_plan(flags, stack, domain, mode)
        elif slug == "replit":
            return _replit_plan(flags, stack, domain, mode)
        # claude_code falls through to default (with git commit additions)

    if mode == "mvp":
        return _mvp_plan(stack, domain)

    entities = _entity_names(domain)
    pages = _page_names(domain)

    plan: List[str] = []

    # ── Phase 1: Foundation ──────────────────────────────────────────
    foundation_steps = [
        "Phase 1 — Foundation",
        "1.1  Define problem statement, target user personas, and measurable success metrics (DAU, retention, conversion).",
        "1.2  Write detailed user stories for the MVP scope — cover happy paths, edge cases, and error states.",
        "1.3  Design system architecture: service boundaries, data flow diagram, and integration points.",
        f"1.4  Initialise monorepo with backend ({stack.backend.split('+')[0].strip()}) and frontend ({stack.frontend.split('+')[0].strip()}).",
    ]
    if tool and tool.slug == "claude_code":
        foundation_steps.append("1.5  Set up environment configuration (.env files) and secrets management.")
        foundation_steps.append("1.6  git commit -m 'Phase 1: project foundation and initial setup'")
    else:
        foundation_steps.append("1.5  Configure CI pipeline: linting (ruff + eslint), type checking, and automated test runner.")
        foundation_steps.append("1.6  Set up environment configuration (.env files) and secrets management.")
    plan.extend(foundation_steps)

    # ── Phase 2: Core Backend ────────────────────────────────────────
    models_step = f"2.3  Build domain models: {entities} (SQLAlchemy) with relationships, indexes, and validation." if entities else "2.3  Build core domain models (SQLAlchemy) with relationships, indexes, and validation."
    service_step = f"2.4  Implement service layer with business logic for: {entities}." if entities else "2.4  Implement service layer with business logic for each domain entity."

    # Build endpoint details from domain
    endpoint_detail = ""
    if domain and "api_endpoints" in domain:
        ep_summary = ", ".join(f"{e['method']} {e['path']}" for e in domain["api_endpoints"][:6])
        if len(domain["api_endpoints"]) > 6:
            ep_summary += f", and {len(domain['api_endpoints']) - 6} more"
        endpoint_detail = f" Endpoints: {ep_summary}."

    route_step = f"2.5  Build REST API routes with Pydantic request/response schemas, pagination, and filtering.{endpoint_detail}"

    plan.extend([
        "Phase 2 — Core Backend",
        f"2.1  Design and create database schema with Alembic migrations for {stack.database.split('+')[0].strip()}."
        + (f" Tables: {entities}." if entities else ""),
        f"2.2  Implement authentication system using {stack.auth}: register, login, refresh, logout, password reset.",
        models_step,
        service_step,
        route_step,
        "2.6  Add middleware: CORS, global error handler, rate limiting, request logging.",
    ])

    # ── Phase 3: Core Frontend ───────────────────────────────────────
    pages_step = f"3.5  Build application pages: {pages} — with forms (react-hook-form + zod), loading states, and empty states." if pages else "3.5  Build core application pages with forms (react-hook-form + zod), loading states, and empty states."

    plan.extend([
        "Phase 3 — Core Frontend",
        f"3.1  Set up {stack.frontend} project with {stack.frontend_ui} component library.",
        "3.2  Build auth pages (login, register, forgot password) and AuthProvider context.",
        "3.3  Build authenticated layout: sidebar navigation, header with user menu, responsive shell.",
        "3.4  Implement API client layer with auth header injection, error handling, and token refresh.",
        pages_step,
        "3.6  Implement toast notifications, confirmation dialogs, and global error boundary.",
    ])

    # ── Phase 4: Feature-Specific ────────────────────────────────────
    feature_steps = []
    step = 1
    if "realtime" in flags:
        feature_steps.append(
            f"4.{step}  Implement real-time layer: WebSocket endpoint, connection manager, "
            f"Redis pub/sub, and frontend useWebSocket hook with auto-reconnect."
        )
        step += 1
    if "payments" in flags:
        feature_steps.append(
            f"4.{step}  Integrate Stripe: create customers, checkout sessions, webhook handler "
            f"(subscription lifecycle), pricing page, and billing portal."
        )
        step += 1
    if "ai" in flags:
        feature_steps.append(
            f"4.{step}  Build AI integration: LLM service with streaming, prompt manager, "
            f"RAG pipeline (if applicable), and frontend streaming UI component."
        )
        step += 1
    if "file_upload" in flags:
        feature_steps.append(
            f"4.{step}  Build file upload system: presigned URL flow, image processing "
            f"(thumbnails, WebP), drag-and-drop UI with progress indicator."
        )
        step += 1
    if "search" in flags:
        feature_steps.append(
            f"4.{step}  Implement search: set up {stack.search}, indexing pipeline, "
            f"search API with facets, and frontend search bar with autocomplete."
        )
        step += 1
    if "notifications" in flags:
        feature_steps.append(
            f"4.{step}  Build notification system: in-app notifications, email via {stack.email}, "
            f"notification preferences, and real-time delivery."
        )
        step += 1
    if "social" in flags:
        feature_steps.append(
            f"4.{step}  Build social features: user profiles, activity feed, comments with "
            f"threading, reactions, follow/unfollow, and content moderation."
        )
        step += 1
    if "scheduling" in flags:
        feature_steps.append(
            f"4.{step}  Build scheduling system: calendar view, availability management, "
            f"booking flow with conflict detection, and email reminders."
        )
        step += 1
    if "analytics" in flags:
        feature_steps.append(
            f"4.{step}  Build analytics dashboard: aggregation queries, Recharts visualisations "
            f"(line, bar, pie), stat cards, and date range filtering."
        )
        step += 1
    if "admin_panel" in flags:
        feature_steps.append(
            f"4.{step}  Build admin panel: user management, content moderation, "
            f"system configuration, and activity audit log."
        )
        step += 1
    if "multi_tenancy" in flags:
        feature_steps.append(
            f"4.{step}  Implement multi-tenancy: organisation model, tenant-scoped queries, "
            f"invite flow, and role-based access within organisations."
        )
        step += 1
    if "auth_advanced" in flags:
        feature_steps.append(
            f"4.{step}  Implement advanced auth: OAuth social login (Google + GitHub), "
            f"2FA/MFA with TOTP, RBAC with fine-grained permissions."
        )
        step += 1
    if "i18n" in flags:
        feature_steps.append(
            f"4.{step}  Add internationalisation: next-intl setup, translation files, "
            f"locale switcher, RTL support, and date/number formatting."
        )
        step += 1
    if "geolocation" in flags:
        feature_steps.append(
            f"4.{step}  Implement geolocation features: map component (Mapbox/Leaflet), "
            f"address autocomplete, proximity search, and distance calculation."
        )
        step += 1
    if "mobile" in flags:
        feature_steps.append(
            f"4.{step}  Build mobile-optimised API: composite endpoints, cursor pagination, "
            f"push notifications (FCM), and sync endpoint for offline-first."
        )
        step += 1

    if feature_steps:
        plan.append("Phase 4 — Feature Integration")
        plan.extend(feature_steps)

    # ── Phase 5: Quality & Launch ────────────────────────────────────
    if tool and tool.slug == "claude_code":
        plan.extend([
            "Phase 5 — Quality & Launch",
            "5.1  Write backend test suite: unit tests for services, integration tests for API routes (pytest + httpx).",
            "5.2  Write frontend tests: component tests (Jest + RTL) and E2E user flow tests (Playwright).",
            "5.3  Security review: OWASP top-10 checklist, dependency audit (pip-audit + npm audit), pen test critical flows.",
            "5.4  Performance optimisation: database query analysis (EXPLAIN), frontend bundle analysis, add caching where needed.",
            "5.5  Build Docker images, finalise docker-compose, and write CI/CD pipeline (GitHub Actions).",
            "5.6  git commit -m 'Phase 5: tests, security, and deployment config'",
            "5.7  Deploy to staging, run full QA pass, fix issues.",
            "5.8  Deploy to production, configure monitoring (Sentry + uptime), and set up alerting.",
            "5.9  Launch beta: gather user feedback, prioritise iteration backlog.",
        ])
    else:
        plan.extend([
            "Phase 5 — Quality & Launch",
            "5.1  Write backend test suite: unit tests for services, integration tests for API routes (pytest + httpx).",
            "5.2  Write frontend tests: component tests (Jest + RTL) and E2E user flow tests (Playwright).",
            "5.3  Security review: OWASP top-10 checklist, dependency audit (pip-audit + npm audit), pen test critical flows.",
            "5.4  Performance optimisation: database query analysis (EXPLAIN), frontend bundle analysis, add caching where needed.",
            "5.5  Build Docker images, finalise docker-compose, and write CI/CD pipeline (GitHub Actions).",
            "5.6  Deploy to staging, run full QA pass, fix issues.",
            "5.7  Deploy to production, configure monitoring (Sentry + uptime), and set up alerting.",
            "5.8  Launch beta: gather user feedback, prioritise iteration backlog.",
        ])

    return plan


# ===================================================================
# TOOL-SPECIFIC PLANS
# ===================================================================

def _lovable_plan(flags: Set[str], stack: StackChoice, domain: Optional[Dict], mode: str) -> List[str]:
    """Implementation plan for Lovable (React + Supabase)."""
    entities = _entity_names(domain)
    pages = _page_names(domain)

    if mode == "mvp":
        plan = [
            "1. Set up new Lovable project and configure Supabase connection.",
            f"2. Design Supabase database tables and RLS policies.{' Tables: ' + entities + '.' if entities else ''}",
            "3. Configure Supabase Auth (email/password sign-up).",
            f"4. Build frontend pages with React + shadcn/ui.{' Pages: ' + pages + '.' if pages else ''}",
            "5. Connect frontend to Supabase client for data fetching and auth.",
            "6. Test end-to-end: auth flow and core feature.",
            "7. Deploy via Lovable's built-in hosting.",
        ]
        return plan

    plan = [
        "Phase 1 — Supabase Setup",
        "1.1  Create new Lovable project and connect Supabase instance.",
        f"1.2  Design and create all database tables in Supabase SQL Editor.{' Tables: ' + entities + '.' if entities else ''}",
        "1.3  Write Row-Level Security (RLS) policies for every table.",
        "1.4  Configure Supabase Auth: email/password, OAuth providers if needed.",
        "1.5  Set up Supabase Storage buckets with RLS (if file uploads needed).",
        "Phase 2 — Core Frontend",
        "2.1  Set up React + Vite + Tailwind + shadcn/ui project structure.",
        "2.2  Build auth pages: Login, Register with Supabase Auth integration.",
        "2.3  Build authenticated layout: sidebar, header, auth guard.",
        f"2.4  Build core application pages.{' Pages: ' + pages + '.' if pages else ''}",
        "2.5  Implement data fetching with Supabase client (`.from().select()`).",
        "2.6  Add forms with react-hook-form + zod validation.",
        "Phase 3 — Features & Polish",
    ]

    step = 1
    if "realtime" in flags:
        plan.append(f"3.{step}  Enable Supabase Realtime on relevant tables for live updates.")
        step += 1
    if "payments" in flags:
        plan.append(f"3.{step}  Create Supabase Edge Function for Stripe checkout and webhooks.")
        step += 1
    if "ai" in flags:
        plan.append(f"3.{step}  Create Supabase Edge Function for OpenAI API integration.")
        step += 1
    if "file_upload" in flags:
        plan.append(f"3.{step}  Implement file uploads with Supabase Storage.")
        step += 1
    if step == 1:
        plan.append("3.1  Add toast notifications, loading states, error handling.")
        step += 1
    plan.append(f"3.{step}  Polish UI: responsive design, empty states, error boundaries.")
    step += 1

    plan.extend([
        "Phase 4 — Testing & Launch",
        "4.1  Test all user workflows end-to-end.",
        "4.2  Verify RLS policies block unauthorized access.",
        "4.3  Deploy via Lovable's built-in hosting.",
    ])

    return plan


def _replit_plan(flags: Set[str], stack: StackChoice, domain: Optional[Dict], mode: str) -> List[str]:
    """Implementation plan for Replit Agent (Node.js + Express + React)."""
    entities = _entity_names(domain)
    pages = _page_names(domain)

    if mode == "mvp":
        return [
            "1. Set up Replit project with Node.js + Express backend and React + Vite frontend.",
            f"2. Define Prisma schema and run initial migration.{' Models: ' + entities + '.' if entities else ''}",
            "3. Build Express API routes: JWT auth (register + login) and CRUD endpoints.",
            f"4. Build React frontend: auth pages, dashboard, and core feature.{' Pages: ' + pages + '.' if pages else ''}",
            "5. Connect frontend to backend API with fetch wrapper.",
            "6. Test locally — verify auth flow and core feature.",
            "7. Deploy via Replit Deployments.",
        ]

    plan = [
        "Phase 1 — Foundation",
        "1.1  Initialise Replit project with Express backend and React + Vite frontend.",
        f"1.2  Define Prisma schema with all models and run `prisma migrate dev`.{' Models: ' + entities + '.' if entities else ''}",
        "1.3  Set up environment variables in Replit Secrets.",
        "Phase 2 — Backend",
        "2.1  Build Express app: CORS, JSON parsing, error handling middleware.",
        "2.2  Implement JWT auth: register (bcrypt hash), login (verify + return JWT).",
        f"2.3  Build CRUD routes for each domain entity.{' Entities: ' + entities + '.' if entities else ''}",
        "2.4  Add input validation (express-validator or zod).",
        "2.5  Add pagination support (?page=1&limit=20).",
        "Phase 3 — Frontend",
        "3.1  Set up React + Vite + Tailwind + shadcn/ui.",
        "3.2  Build auth pages (login, register) and AuthContext.",
        "3.3  Build authenticated layout: sidebar, header.",
        f"3.4  Build application pages.{' Pages: ' + pages + '.' if pages else ''}",
        "3.5  Implement API client with auth header injection.",
        "3.6  Add forms, loading states, error handling, toast notifications.",
    ]

    feature_steps = []
    step = 1
    if "realtime" in flags:
        feature_steps.append(f"4.{step}  Add Socket.io for real-time features.")
        step += 1
    if "payments" in flags:
        feature_steps.append(f"4.{step}  Integrate Stripe: checkout sessions, webhook handler.")
        step += 1
    if "ai" in flags:
        feature_steps.append(f"4.{step}  Integrate OpenAI npm package for AI features.")
        step += 1

    if feature_steps:
        plan.append("Phase 4 — Feature Integration")
        plan.extend(feature_steps)

    plan.extend([
        f"Phase {'5' if feature_steps else '4'} — Quality & Launch",
        f"{'5' if feature_steps else '4'}.1  Test all user flows end-to-end.",
        f"{'5' if feature_steps else '4'}.2  Add basic error handling and input validation.",
        f"{'5' if feature_steps else '4'}.3  Deploy via Replit Deployments.",
    ])

    return plan


def _base44_plan(flags: Set[str], stack: StackChoice, domain: Optional[Dict], mode: str) -> List[str]:
    """Implementation plan for Base44 (no-code data-first platform)."""
    entities = _entity_names(domain)
    pages = _page_names(domain)

    if mode == "mvp":
        return [
            f"1. Define core entities in Base44.{' Entities: ' + entities + '.' if entities else ''}",
            "2. Configure entity fields, types, and relations.",
            f"3. Create pages for each entity.{' Pages: ' + pages + '.' if pages else ''}",
            "4. Set up authentication and user roles.",
            "5. Test the app in Base44 preview.",
            "6. Publish via Base44 hosting.",
        ]

    return [
        "Phase 1 — Entity Design",
        f"1.1  Define all entities with fields and types.{' Entities: ' + entities + '.' if entities else ''}",
        "1.2  Configure relations between entities (one-to-many, many-to-many).",
        "1.3  Set display fields and default sort for each entity.",
        "Phase 2 — Page Design",
        f"2.1  Create List pages for each entity.{' Pages: ' + pages + '.' if pages else ''}",
        "2.2  Create Detail/Form pages for viewing and editing records.",
        "2.3  Create a Dashboard page with stat cards and charts.",
        "2.4  Configure filters, search, and sorting on List pages.",
        "Phase 3 — Workflows & Auth",
        "3.1  Define automation rules (on create, on update triggers).",
        "3.2  Configure user roles and permissions per entity/page.",
        "3.3  Set up email notifications for key events.",
        "Phase 4 — Testing & Launch",
        "4.1  Test all workflows in Base44 preview mode.",
        "4.2  Verify role-based access control.",
        "4.3  Publish via Base44 hosting.",
    ]
