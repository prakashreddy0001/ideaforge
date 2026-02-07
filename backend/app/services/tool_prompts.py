"""Tool-specific prompt builders.

Each AI coding tool (Lovable, Replit, Base44, Claude Code) gets its own
master prompt and set of individual prompts tailored to the tool's stack,
conventions, and prompt style.
"""

from typing import Dict, List, Optional, Set

from app.services.stack_selection import StackChoice
from app.services.prompt_templates import (
    _stack_block,
    _domain_entities_block,
    _domain_endpoints_block,
    _domain_pages_block,
    _domain_workflows_block,
    _QUALITY_FOOTER,
)


# ===================================================================
# LOVABLE — React + Vite + Supabase
# ===================================================================

def _lovable_master(
    idea: str, target_users: Optional[str], flags: Set[str],
    stack: StackChoice, domain: Optional[Dict], mode: str,
) -> str:
    entities = _domain_entities_block(domain)
    endpoints = _domain_endpoints_block(domain)
    pages = _domain_pages_block(domain)
    workflows = _domain_workflows_block(domain)

    feature_notes = ""
    if "realtime" in flags:
        feature_notes += "\n- Enable Supabase Realtime on relevant tables for live updates."
    if "payments" in flags:
        feature_notes += "\n- Integrate Stripe via Supabase Edge Function (webhook handler + checkout session)."
    if "ai" in flags:
        feature_notes += "\n- Call OpenAI API from a Supabase Edge Function; stream responses via SSE."
    if "file_upload" in flags:
        feature_notes += "\n- Use Supabase Storage for file uploads with RLS policies on buckets."
    if "search" in flags:
        feature_notes += "\n- Use PostgreSQL full-text search (tsvector) for search functionality."

    lean = mode == "mvp"
    scope = "MVP" if lean else "production-ready"

    return f"""Build a **complete, {scope}** web application using **Lovable** (lovable.dev).
Lovable generates React + Vite + Tailwind CSS apps with Supabase as the backend.
Describe EVERYTHING the app needs so Lovable can build it in one shot.

## Project Description
{idea}
{f"**Target Users:** {target_users}" if target_users else ""}

## Tech Stack (Lovable's stack)
- **Frontend:** React 18 + Vite 5 + Tailwind CSS 3 + shadcn/ui
- **Backend:** Supabase (PostgreSQL database, Auth, Edge Functions, Storage, Realtime)
- **Hosting:** Lovable auto-deploy
{entities}
{pages}
{workflows}

## Supabase Database Design
Define ALL tables the app needs. For each table:
- Table name, columns with types (uuid, text, int4, bool, timestamptz, jsonb)
- Primary keys, foreign keys, and relationships
- Row-Level Security (RLS) policies: who can SELECT, INSERT, UPDATE, DELETE
- Enable Realtime on tables that need live updates
{endpoints if not lean else ""}

## Authentication
- Use Supabase Auth with email/password sign-up
- Protected routes redirect to login if not authenticated
- Auth state managed via Supabase client `onAuthStateChange`

## Frontend Pages & Components
{"Build all pages listed above." if pages else "Build pages for every core workflow."}
Each page needs:
- Loading states, error handling, empty states
- Responsive design (mobile-first)
- Forms with validation using react-hook-form + zod
- Toast notifications for success/error feedback
{f"## Feature-Specific Requirements{feature_notes}" if feature_notes else ""}

## Important Lovable Conventions
- Do NOT generate a separate backend server — Supabase handles all backend logic
- Use Supabase client library (`@supabase/supabase-js`) for all data operations
- For custom server-side logic, use Supabase Edge Functions (Deno/TypeScript)
- All database access must go through RLS policies — never disable RLS
- Use Supabase Storage for file handling, not external S3
{"- Keep it lean — only essential features for MVP" if lean else "- Build for production: proper error handling, loading states, and edge cases"}"""


def _lovable_frontend(
    idea: str, target_users: Optional[str], flags: Set[str],
    stack: StackChoice, domain: Optional[Dict],
) -> str:
    pages = _domain_pages_block(domain)
    workflows = _domain_workflows_block(domain)

    return f"""You are building the React frontend for a Lovable app.
Describe the **complete component and page structure**.

## App Idea
{idea}
{f"Target Users: {target_users}" if target_users else ""}

## Tech Stack
- React 18 + Vite 5 + Tailwind CSS 3 + shadcn/ui
- Supabase client for data fetching and auth
- react-hook-form + zod for forms
- React Router for navigation
{pages}
{workflows}

## Page Structure
For each page, describe:
- Route path
- What data it displays (which Supabase table/query)
- User interactions (forms, buttons, modals)
- Loading, error, and empty states

## Component Architecture
- Reusable UI components (Button, Card, Modal, DataTable, etc.)
- Domain-specific components (e.g., TaskCard, ProjectBoard)
- Layout components (Sidebar, Header, AuthGuard)

## Authentication Flow
- Login page → Supabase signInWithPassword → redirect to dashboard
- Register page → Supabase signUp → email confirmation → redirect
- AuthGuard component wraps protected routes
- Logout via Supabase signOut

## Data Fetching
- Use Supabase client's `.from('table').select()` for reads
- Use `.insert()`, `.update()`, `.delete()` for writes
- Subscribe to Realtime changes where needed
- Handle optimistic updates for better UX
{_QUALITY_FOOTER}"""


def _lovable_database(
    idea: str, flags: Set[str], stack: StackChoice, domain: Optional[Dict],
) -> str:
    entities = _domain_entities_block(domain)

    return f"""You are designing the Supabase PostgreSQL database for a Lovable app.
Produce **COMPLETE SQL** for all tables, RLS policies, and triggers.

## App Idea
{idea}
{entities}

## Requirements

1. **Tables** — Create all tables listed above. For each:
   - Use `uuid` primary keys with `gen_random_uuid()` default
   - Add `created_at timestamptz default now()` and `updated_at timestamptz`
   - Define foreign keys with ON DELETE behavior
   - Add indexes on columns used in WHERE/ORDER BY

2. **Row-Level Security (RLS)** — For EVERY table:
   - Enable RLS: `ALTER TABLE ... ENABLE ROW LEVEL SECURITY;`
   - SELECT policy: users can read their own data (or public data)
   - INSERT policy: authenticated users can insert their own rows
   - UPDATE policy: users can only update their own rows
   - DELETE policy: users can only delete their own rows
   - Use `auth.uid()` to reference the current user's ID

3. **Supabase Auth Integration**
   - User profiles table linked to `auth.users` via trigger
   - On new sign-up, auto-create a profile row

4. **Realtime** (if applicable)
   - Enable Supabase Realtime on tables that need live updates:
     `ALTER PUBLICATION supabase_realtime ADD TABLE ...;`

Output complete SQL that can be pasted into the Supabase SQL Editor.
{_QUALITY_FOOTER}"""


def build_lovable_prompts(
    idea: str, flags: Set[str], stack: StackChoice,
    target_users: Optional[str], domain: Optional[Dict], mode: str,
) -> Dict[str, str]:
    prompts: Dict[str, str] = {}
    prompts["master_prompt"] = _lovable_master(idea, target_users, flags, stack, domain, mode)
    prompts["frontend_code"] = _lovable_frontend(idea, target_users, flags, stack, domain)
    prompts["database_schema"] = _lovable_database(idea, flags, stack, domain)
    return prompts


# ===================================================================
# REPLIT AGENT — React + Node.js/Express + PostgreSQL
# ===================================================================

def _replit_master(
    idea: str, target_users: Optional[str], flags: Set[str],
    stack: StackChoice, domain: Optional[Dict], mode: str,
) -> str:
    entities = _domain_entities_block(domain)
    endpoints = _domain_endpoints_block(domain)
    pages = _domain_pages_block(domain)
    workflows = _domain_workflows_block(domain)

    feature_notes = ""
    if "realtime" in flags:
        feature_notes += "\n- Use Socket.io for real-time features (Express + React)."
    if "payments" in flags:
        feature_notes += "\n- Integrate Stripe: checkout sessions, webhook handler, billing portal."
    if "ai" in flags:
        feature_notes += "\n- Use OpenAI npm package for AI features; stream responses via SSE."
    if "file_upload" in flags:
        feature_notes += "\n- Use multer for file uploads; store in Replit Object Storage."

    lean = mode == "mvp"
    scope = "MVP" if lean else "production-ready"

    return f"""Build a **complete, {scope}** full-stack web application using **Replit Agent**.
Replit uses React for the frontend and Node.js + Express for the backend with PostgreSQL.

## Project Description
{idea}
{f"**Target Users:** {target_users}" if target_users else ""}

## Tech Stack (Replit's stack)
- **Frontend:** React 18 + Vite + Tailwind CSS 3 + shadcn/ui
- **Backend:** Node.js 20 + Express 4
- **Database:** PostgreSQL 16 + Prisma ORM
- **Auth:** Express sessions + bcrypt + JWT
- **Hosting:** Replit Deployments (auto-hosted)
{entities}
{endpoints}
{pages}
{workflows}

## Backend Structure
```
server/
  index.js              # Express app setup, middleware, routes
  routes/
    auth.js             # POST /auth/register, POST /auth/login, POST /auth/logout
    [domain].js         # CRUD routes per entity
  models/
    prisma/schema.prisma # Prisma schema with all models
  middleware/
    auth.js             # JWT verification middleware
  .env
```

## Frontend Structure
```
client/
  src/
    App.jsx             # Router setup
    pages/              # Page components
    components/         # Reusable UI components
    lib/
      api.js            # Fetch wrapper with auth headers
      auth.jsx          # Auth context + provider
  index.html
```

## Authentication
- Register: hash password with bcrypt, store in DB, return JWT
- Login: verify credentials, return JWT
- JWT stored in localStorage; sent as Bearer token in Authorization header
- Auth middleware verifies JWT on protected routes

## Database (Prisma)
- Define all models in `prisma/schema.prisma`
- Use UUID primary keys
- Run `prisma migrate dev` for migrations
- Seed script for development data
{f"## Feature-Specific{feature_notes}" if feature_notes else ""}

## Replit Conventions
- Keep file structure flat and simple
- Use a single `server/index.js` entry point
- Do NOT create Docker files or CI/CD pipelines — Replit handles deployment
- Use environment variables via Replit Secrets (not .env files in production)
- The app should work on port 3000 (Replit's default)
{"- MVP only — skip tests, monitoring, and advanced features" if lean else ""}
{_QUALITY_FOOTER}"""


def _replit_backend(
    idea: str, target_users: Optional[str], flags: Set[str],
    stack: StackChoice, domain: Optional[Dict],
) -> str:
    entities = _domain_entities_block(domain)
    endpoints = _domain_endpoints_block(domain)

    return f"""You are a Node.js backend engineer. Build a **COMPLETE Express backend** for Replit.

## App Idea
{idea}
{f"Target Users: {target_users}" if target_users else ""}

## Tech Stack
- Node.js 20 + Express 4
- PostgreSQL + Prisma ORM
- bcrypt for password hashing
- jsonwebtoken for JWT
{entities}
{endpoints}

## File Structure (flat, Replit-friendly)
```
server/
  index.js              # Express app: cors, json parsing, routes, error handler
  routes/auth.js        # Register, login, logout
  routes/[entity].js    # CRUD per domain entity
  middleware/auth.js     # JWT verify middleware
  prisma/schema.prisma  # All Prisma models
  seed.js               # Seed script
```

## Requirements
- RESTful JSON API
- JWT auth: register → hash password → return token; login → verify → return token
- CRUD for every entity listed above
- Input validation using express-validator or zod
- Error handling middleware (return JSON errors, never stack traces)
- Pagination: `?page=1&limit=20`
{_QUALITY_FOOTER}"""


def _replit_frontend(
    idea: str, target_users: Optional[str], flags: Set[str],
    stack: StackChoice, domain: Optional[Dict],
) -> str:
    pages = _domain_pages_block(domain)

    return f"""You are a React frontend engineer. Build a **COMPLETE frontend** for a Replit app.

## App Idea
{idea}
{f"Target Users: {target_users}" if target_users else ""}

## Tech Stack
- React 18 + Vite + Tailwind CSS 3 + shadcn/ui
- react-hook-form + zod for forms
- Fetch API with auth wrapper
{pages}

## File Structure
```
client/src/
  App.jsx               # React Router setup
  pages/
    Landing.jsx
    Login.jsx
    Register.jsx
    Dashboard.jsx        # Main app page
    [domain pages]
  components/
    ui/                  # Button, Card, Input, Modal
    layouts/             # Sidebar, Header
  lib/
    api.js               # Fetch wrapper: adds auth header, handles 401
    auth.jsx             # AuthContext: user state, login/register/logout
```

## Requirements
- Auth flow: register → login → redirect to dashboard
- Protected routes redirect to login if not authenticated
- Loading spinners, error states, empty states
- Mobile-responsive with Tailwind
- Toast notifications for actions
{_QUALITY_FOOTER}"""


def _replit_database(
    idea: str, flags: Set[str], stack: StackChoice, domain: Optional[Dict],
) -> str:
    entities = _domain_entities_block(domain)

    return f"""You are a database engineer. Design a **Prisma schema** for a Replit app.

## App Idea
{idea}
{entities}

## Requirements
- Use Prisma ORM with PostgreSQL
- Output a complete `prisma/schema.prisma` file
- UUID primary keys: `id String @id @default(uuid())`
- `createdAt DateTime @default(now())` and `updatedAt DateTime @updatedAt`
- Define all relations with `@relation`
- Add `@@index` for query-optimized fields
- Include a seed script (`server/seed.js`) with sample data
{_QUALITY_FOOTER}"""


def build_replit_prompts(
    idea: str, flags: Set[str], stack: StackChoice,
    target_users: Optional[str], domain: Optional[Dict], mode: str,
) -> Dict[str, str]:
    prompts: Dict[str, str] = {}
    prompts["master_prompt"] = _replit_master(idea, target_users, flags, stack, domain, mode)
    prompts["backend_code"] = _replit_backend(idea, target_users, flags, stack, domain)
    prompts["frontend_code"] = _replit_frontend(idea, target_users, flags, stack, domain)
    prompts["database_schema"] = _replit_database(idea, flags, stack, domain)
    return prompts


# ===================================================================
# BASE44 — No-code data-first platform
# ===================================================================

def _base44_master(
    idea: str, target_users: Optional[str], flags: Set[str],
    stack: StackChoice, domain: Optional[Dict], mode: str,
) -> str:
    entities = _domain_entities_block(domain)
    pages = _domain_pages_block(domain)
    workflows = _domain_workflows_block(domain)

    integrations = ""
    if "payments" in flags:
        integrations += "\n- **Stripe**: Connect for payment processing, subscriptions, invoicing."
    if "ai" in flags:
        integrations += "\n- **OpenAI**: Connect for AI-powered features (text generation, analysis)."
    if "notifications" in flags or "email" in flags:
        integrations += "\n- **SendGrid/Resend**: Connect for transactional emails and notifications."

    lean = mode == "mvp"

    return f"""Build a **complete application** using **Base44** (base44.com).
Base44 is a data-first AI app builder — you define entities and pages, and it generates everything.
Do NOT write code. Instead, describe the data model, pages, and workflows.

## Project Description
{idea}
{f"**Target Users:** {target_users}" if target_users else ""}
{entities}
{pages}
{workflows}

## Entity Definitions (Base44 format)
For each entity, define:
- **Name** (singular, PascalCase)
- **Fields** with types: Text, Number, Boolean, Date, DateTime, Email, URL, Image, File, Relation, Select, MultiSelect, JSON
- **Relations**: which entities are linked (one-to-many, many-to-many)
- **Display field**: which field shows as the entity's label
- **Default sort**: which field to sort by

## Page Definitions
For each page, define:
- **Page name** and route
- **Type**: List (data table), Detail (single record), Form (create/edit), Dashboard (charts/stats), Custom
- **Data source**: which entity this page displays
- **Visible columns/fields**: which fields to show
- **Actions**: Create, Edit, Delete, custom buttons
- **Filters**: which fields users can filter by

## Workflow / Automation Rules
Define automation rules:
- **Trigger**: on entity create, update, delete, or scheduled
- **Condition**: field equals, contains, greater than, etc.
- **Action**: send email, update field, create related record, call webhook
{f"## Integrations{integrations}" if integrations else ""}

## Authentication & Roles
- Define user roles (e.g., Admin, Member, Viewer)
- For each entity/page, define which roles have access
- Define which fields are visible per role

## Base44 Conventions
- Do NOT write any code — Base44 generates everything
- Focus on clear entity definitions with proper field types
- Use Relations to link entities (not foreign key fields)
- Use Select/MultiSelect for enum-like fields (e.g., status, priority)
- Use the Workflow builder for business logic, not code
{"- MVP: only include essential entities and pages" if lean else "- Include all entities, pages, and workflows for a complete app"}"""


def _base44_entities(
    idea: str, flags: Set[str], domain: Optional[Dict],
) -> str:
    entities = _domain_entities_block(domain)

    return f"""Define the **complete entity model** for a Base44 app.

## App Idea
{idea}
{entities}

## For Each Entity, Provide:

### Entity Name (PascalCase)
- **Description**: What this entity represents
- **Fields**:
  | Field Name | Type | Required | Default | Notes |
  |------------|------|----------|---------|-------|
  | name | Text | Yes | - | Display field |
  | status | Select | Yes | "active" | Options: active, inactive, archived |
  | ... | ... | ... | ... | ... |
- **Relations**:
  - belongsTo: [Parent Entity] (many-to-one)
  - hasMany: [Child Entity] (one-to-many)
- **Display Field**: which field is the entity label
- **Default Sort**: which field, ascending or descending

## Field Type Reference
- **Text**: short text (title, name)
- **LongText**: multi-line text (description, notes)
- **Number**: integer or decimal
- **Boolean**: true/false toggle
- **Date**: date only
- **DateTime**: date + time
- **Email**: validated email
- **URL**: validated URL
- **Image**: image upload
- **File**: file upload
- **Relation**: link to another entity
- **Select**: single choice from predefined options
- **MultiSelect**: multiple choices
- **JSON**: structured data"""


def _base44_pages(
    idea: str, domain: Optional[Dict],
) -> str:
    pages = _domain_pages_block(domain)
    workflows = _domain_workflows_block(domain)

    return f"""Define the **complete page layout** for a Base44 app.

## App Idea
{idea}
{pages}
{workflows}

## For Each Page, Provide:

### Page Name
- **Route**: `/path`
- **Type**: List | Detail | Form | Dashboard | Custom
- **Data Source**: which entity
- **Layout**:
  - Columns/fields to display
  - Sort order
  - Filters available to users
  - Search enabled: yes/no
- **Actions**:
  - Create button: yes/no
  - Row actions: Edit, Delete, View, custom
  - Bulk actions: Delete, Export
- **Access**: which roles can view this page

## Dashboard Pages
For dashboard/analytics pages:
- Define stat cards (label, value source, icon)
- Define charts (type: bar/line/pie, data source, x-axis, y-axis)
- Define date range filter"""


def build_base44_prompts(
    idea: str, flags: Set[str], stack: StackChoice,
    target_users: Optional[str], domain: Optional[Dict], mode: str,
) -> Dict[str, str]:
    prompts: Dict[str, str] = {}
    prompts["master_prompt"] = _base44_master(idea, target_users, flags, stack, domain, mode)
    prompts["entity_design"] = _base44_entities(idea, flags, domain)
    prompts["page_design"] = _base44_pages(idea, domain)
    return prompts


# ===================================================================
# CLAUDE CODE — FastAPI + Next.js (detailed code generation)
# ===================================================================

def _claude_code_master(
    idea: str, target_users: Optional[str], flags: Set[str],
    stack: StackChoice, industry: Optional[str],
    domain: Optional[Dict], mode: str,
) -> str:
    entities = _domain_entities_block(domain)
    endpoints = _domain_endpoints_block(domain)
    pages = _domain_pages_block(domain)
    workflows = _domain_workflows_block(domain)

    feature_sections = ""
    if "realtime" in flags:
        feature_sections += """
### Real-Time Features
- WebSocket endpoint at `/ws?token=<jwt>` with connection manager and Redis pub/sub
- Frontend `useWebSocket` hook with auto-reconnect
"""
    if "payments" in flags:
        feature_sections += """
### Stripe Integration
- Checkout sessions, webhook handler, billing portal, subscription management
"""
    if "ai" in flags:
        feature_sections += """
### AI Integration
- LLM service with streaming, prompt manager, SSE endpoint
"""

    lean = mode == "mvp"
    scope = "MVP" if lean else "COMPLETE, PRODUCTION-READY"

    return f"""You are using **Claude Code** (Anthropic's CLI tool) to build a {scope} application.
Generate every file needed. Use the Write tool to create each file, then run the project to verify.

## Workflow Instructions for Claude Code
1. Create the project directory structure first
2. Write backend files one at a time (models → schemas → services → routes → main.py)
3. Write frontend files (layout → pages → components → lib)
4. Run `pip install -r requirements.txt` and `npm install` to install dependencies
5. Run `alembic upgrade head` to create database tables
6. Start the backend with `uvicorn app.main:app --reload` and verify /health endpoint
7. Start the frontend with `npm run dev` and test the auth flow
8. Commit with git after each major phase

## Project Description
{idea}
{f"**Target Users:** {target_users}" if target_users else ""}
{f"**Industry:** {industry}" if industry else ""}

## Tech Stack
{_stack_block(stack)}
{entities}
{endpoints}
{pages}
{workflows}

## Backend (FastAPI + Python)
- Use SQLAlchemy 2.0 async with `mapped_column`
- JWT auth: access token (15 min) + refresh token (7 days)
- Pydantic schemas for request/response validation
- Alembic for migrations
- Global error handler returning JSON

## Frontend (Next.js 14)
- App Router with authenticated layout
- react-hook-form + zod for forms
- Central API client with auth header injection
- Loading states, error states, empty states
- Responsive design with Tailwind
{f"## Feature Integrations{feature_sections}" if feature_sections else ""}

## Deployment
- `backend/Dockerfile` + `frontend/Dockerfile` (multi-stage)
- `docker-compose.yml` for local dev
- `.github/workflows/ci.yml` for CI/CD

## Quality
- All code COMPLETE — no TODOs or placeholders
- Full error handling, input validation, logging
- Type hints throughout (Python + TypeScript)
{"- MVP: skip tests, CI/CD, advanced monitoring" if lean else "- Include pytest tests, Jest tests, Playwright E2E"}"""


def build_claude_code_prompts(
    idea: str, flags: Set[str], stack: StackChoice,
    target_users: Optional[str], constraints: Optional[List[str]],
    industry: Optional[str], domain: Optional[Dict], mode: str,
) -> str:
    """Return the Claude Code master prompt only — individual prompts use the default builders."""
    return _claude_code_master(idea, target_users, flags, stack, industry, domain, mode)
