"""AI coding tool profiles.

Each profile defines a fixed tech stack and prompt configuration
for a specific AI coding tool (Lovable, Replit, Base44, Claude Code).
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

from app.services.stack_selection import StackChoice


@dataclass
class ToolProfile:
    slug: str
    name: str
    description: str
    stack: StackChoice
    prompt_style: str          # "descriptive", "conversational", "entity_focused", "detailed_code"
    has_own_deployment: bool
    has_own_auth: bool


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

_LOVABLE = ToolProfile(
    slug="lovable",
    name="Lovable",
    description="React + Vite + Tailwind + Supabase",
    stack=StackChoice(
        frontend="React 18 + Vite 5 + Tailwind CSS 3",
        frontend_ui="shadcn/ui + Radix primitives",
        backend="Supabase Edge Functions (Deno/TypeScript)",
        database="Supabase PostgreSQL (with Row-Level Security)",
        cache="None",
        infra="Lovable hosting (auto-deployed)",
        auth="Supabase Auth (email/password + OAuth)",
        ai="OpenAI GPT-4.1 (via Supabase Edge Function)",
        search="None",
        file_storage="Supabase Storage",
        email="Supabase Edge Function + Resend",
        monitoring="Sentry (frontend only)",
        testing="Vitest + React Testing Library",
    ),
    prompt_style="descriptive",
    has_own_deployment=True,
    has_own_auth=True,
)

_REPLIT = ToolProfile(
    slug="replit",
    name="Replit Agent",
    description="React + Node.js/Express + PostgreSQL",
    stack=StackChoice(
        frontend="React 18 + Vite 5 + Tailwind CSS 3",
        frontend_ui="shadcn/ui + Radix primitives",
        backend="Node.js 20 + Express 4",
        database="PostgreSQL 16 + Prisma ORM",
        cache="None",
        infra="Replit Deployments (auto-hosted)",
        auth="Express sessions + bcrypt + JWT",
        ai="OpenAI GPT-4.1 (via openai npm package)",
        search="None",
        file_storage="Replit Object Storage",
        email="Resend (npm package)",
        monitoring="Console logging + Sentry",
        testing="Jest + Supertest (backend) · Vitest + RTL (frontend)",
    ),
    prompt_style="conversational",
    has_own_deployment=True,
    has_own_auth=False,
)

_BASE44 = ToolProfile(
    slug="base44",
    name="Base44",
    description="No-code data-first AI app builder",
    stack=StackChoice(
        frontend="Base44 auto-generated UI",
        frontend_ui="Base44 built-in components",
        backend="Base44 platform (managed)",
        database="Base44 built-in database",
        cache="None",
        infra="Base44 hosting (managed)",
        auth="Base44 built-in auth",
        ai="Base44 AI (Claude Sonnet 4 / Gemini 2.5 Pro)",
        search="Base44 built-in search",
        file_storage="Base44 file storage",
        email="Base44 integrations (SendGrid / Resend)",
        monitoring="Base44 dashboard",
        testing="Manual testing via Base44 preview",
    ),
    prompt_style="entity_focused",
    has_own_deployment=True,
    has_own_auth=True,
)

_CLAUDE_CODE = ToolProfile(
    slug="claude_code",
    name="Claude Code",
    description="FastAPI + Next.js (full code generation)",
    stack=None,  # Uses choose_stack() dynamically — filled at runtime
    prompt_style="detailed_code",
    has_own_deployment=False,
    has_own_auth=False,
)


TOOL_PROFILES: Dict[str, ToolProfile] = {
    "lovable": _LOVABLE,
    "replit": _REPLIT,
    "base44": _BASE44,
    "claude_code": _CLAUDE_CODE,
}


def get_tool_profile(slug: Optional[str]) -> Optional[ToolProfile]:
    """Return the tool profile for *slug*, or None for default behavior."""
    if not slug:
        return None
    return TOOL_PROFILES.get(slug)
