"""Ideation orchestrator.

Thin coordinator that delegates to specialised modules for feature detection,
stack selection, prompt generation, documentation, and implementation planning.
"""

import json
import logging
import re
from typing import Dict, Optional, Set

from app.api.schemas import IdeaRequest
from app.core.config import settings
from app.providers.openai_provider import OpenAIProvider
from app.services.doc_templates import build_doc_pack
from app.services.feature_detection import detect_features
from app.services.implementation_plan import build_implementation_plan
from app.services.prompt_templates import build_prompt_pack
from app.services.stack_selection import choose_stack
from app.services.system_prompts import build_system_prompt, build_user_prompt
from app.services.tool_profiles import get_tool_profile

logger = logging.getLogger(__name__)


def _extract_json(text: str) -> dict:
    """Parse JSON from *text*, falling back to regex extraction."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("Model did not return JSON.")
        return json.loads(match.group(0))


_REQUIRED_KEYS = {"implementation_plan", "tech_stack", "prompts", "docs"}


def _validate_payload(payload: dict) -> dict:
    if not _REQUIRED_KEYS.issubset(payload.keys()):
        raise ValueError("Model response missing required keys.")
    return payload


_REFINE_SYSTEM = (
    "You are a senior product consultant. The user will give you a rough product idea. "
    "Your job is to REFINE it into a clear, structured description that a developer can act on. "
    "Return ONLY the refined description as plain text (no JSON, no markdown headings). "
    "Include:\n"
    "1. A one-sentence summary of what the product does.\n"
    "2. The core problem it solves and for whom.\n"
    "3. The 3-5 key features that make up the MVP.\n"
    "4. The main user workflows (step by step).\n"
    "5. What makes it different or valuable.\n"
    "Keep it concise — 150-300 words. Do NOT add features the user didn't mention or imply."
)

_DOMAIN_ANALYSIS_SYSTEM = (
    "You are a senior software architect. Analyze the product idea and extract its "
    "concrete domain model so developers can build it.\n"
    "Return ONLY valid JSON (no markdown fences, no commentary) with these exact keys:\n"
    "{\n"
    '  "app_name": "short_project_name_in_snake_case",\n'
    '  "entities": [\n'
    '    {"name": "EntityName", "table_name": "entity_names", '
    '"description": "What this entity represents", '
    '"fields": ["field1", "field2", "field3"]}\n'
    "  ],\n"
    '  "api_endpoints": [\n'
    '    {"method": "POST", "path": "/api/resource", '
    '"description": "What this endpoint does", "auth": "authenticated"}\n'
    "  ],\n"
    '  "pages": [\n'
    '    {"name": "Page Name", "path": "/dashboard/page", '
    '"description": "What the user sees and does on this page"}\n'
    "  ],\n"
    '  "workflows": [\n'
    '    "Step-by-step description of a key user workflow"\n'
    "  ]\n"
    "}\n\n"
    "Rules:\n"
    "- Include 3-8 entities with 4-8 fields each (domain-specific, not just id/timestamps)\n"
    "- Include 10-20 API endpoints covering CRUD + domain-specific actions\n"
    "- Include 5-10 frontend pages the app needs\n"
    "- Include 3-5 key user workflows as step-by-step descriptions\n"
    "- Be SPECIFIC to THIS idea — use actual domain terminology\n"
    "- Do NOT include generic auth endpoints (register/login) — those are handled separately\n"
    "- Entity fields should be domain-meaningful (e.g., 'priority', 'due_date', 'assignee_id'), "
    "not boilerplate (id, created_at are added automatically)"
)

_DOMAIN_ANALYSIS_SYSTEM_MVP = (
    "You are a software architect. Analyze the product idea and extract its core domain model "
    "for an MVP build.\n"
    "Return ONLY valid JSON (no markdown fences) with these keys:\n"
    "{\n"
    '  "app_name": "short_name",\n'
    '  "entities": [{"name": "...", "table_name": "...", "description": "...", '
    '"fields": ["..."]}],\n'
    '  "api_endpoints": [{"method": "...", "path": "...", "description": "...", '
    '"auth": "..."}],\n'
    '  "pages": [{"name": "...", "path": "...", "description": "..."}],\n'
    '  "workflows": ["..."]\n'
    "}\n"
    "Keep it lean: 2-4 entities, 6-10 endpoints, 3-5 pages, 2-3 workflows.\n"
    "Focus on the CORE feature only. Be specific to THIS idea."
)

_REFINE_SYSTEM_MVP = (
    "You are a product consultant. The user will give you a rough product idea. "
    "Refine it into a clear, concise description a developer can build from. "
    "Return ONLY plain text (no JSON, no markdown). "
    "Include: one-sentence summary, core problem, 2-3 key MVP features, main user flow. "
    "Keep it under 100 words. Do NOT add features the user didn't mention."
)


def _analyze_domain(
    provider: OpenAIProvider,
    refined_idea: str,
    target_users: Optional[str],
    mode: str,
) -> Optional[Dict]:
    """Call the LLM to extract a structured domain model from the refined idea."""
    system = _DOMAIN_ANALYSIS_SYSTEM_MVP if mode == "mvp" else _DOMAIN_ANALYSIS_SYSTEM
    user_msg = f"Product idea: {refined_idea}"
    if target_users:
        user_msg += f"\nTarget users: {target_users}"

    max_tok = 1200 if mode == "mvp" else 2500
    try:
        resp = provider.client.chat.completions.create(
            model=provider.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_msg},
            ],
            max_tokens=max_tok,
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        text = (resp.choices[0].message.content or "").strip()
        domain = _extract_json(text)
        # Basic validation
        if "entities" in domain and "api_endpoints" in domain:
            return domain
        logger.warning("Domain analysis missing required keys — skipping")
        return None
    except Exception:
        logger.warning("Domain analysis failed — prompts will use generic templates")
        return None


def _refine_idea(
    provider: OpenAIProvider,
    raw_idea: str,
    target_users: str,
    mode: str,
) -> str:
    """Call the LLM to expand a vague idea into a clear, structured description."""
    system = _REFINE_SYSTEM_MVP if mode == "mvp" else _REFINE_SYSTEM
    user_msg = f"Idea: {raw_idea}"
    if target_users:
        user_msg += f"\nTarget users: {target_users}"

    max_tok = 400 if mode == "mvp" else 800
    try:
        # Use low temperature for factual refinement; disable JSON mode for plain text
        refined = provider.client.chat.completions.create(
            model=provider.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_msg},
            ],
            max_tokens=max_tok,
            temperature=0.4,
        )
        text = (refined.choices[0].message.content or "").strip()
        return text if len(text) > 30 else raw_idea
    except Exception:
        logger.warning("Idea refinement failed — using raw idea")
        return raw_idea


def _estimate_complexity(flags: Set[str]) -> str:
    count = len(flags)
    if count <= 2:
        return "MVP"
    if count <= 5:
        return "Medium"
    return "Complex"


def generate_package(req: IdeaRequest) -> dict:
    """Generate a full ideation package from a user idea."""
    idea = req.idea.strip()
    if len(idea) < 10:
        raise ValueError("Idea is too short.")

    mode = getattr(req, "mode", "production") or "production"

    # 1. Refine the idea via LLM (structured, clear description)
    try:
        provider = OpenAIProvider(settings.openai_api_key, settings.openai_model)
        refined = _refine_idea(provider, idea, req.target_users, mode)
    except Exception:
        logger.warning("Could not create provider for refinement — using raw idea")
        provider = None
        refined = idea

    # 2. Analyse the refined idea (features detected from BOTH raw + refined)
    flags = detect_features(idea) | detect_features(refined)

    # 2a. Load tool profile if user selected a specific AI tool
    tool_profile = get_tool_profile(getattr(req, "tool", None))
    if tool_profile and tool_profile.stack is not None:
        stack = tool_profile.stack
    else:
        stack = choose_stack(flags)
        # For claude_code, fill in the dynamically-chosen stack
        if tool_profile and tool_profile.stack is None:
            tool_profile.stack = stack

    # 2b. Extract domain-specific details (entities, endpoints, pages, workflows)
    domain = None
    try:
        if provider is None:
            provider = OpenAIProvider(settings.openai_api_key, settings.openai_model)
        domain = _analyze_domain(provider, refined, req.target_users, mode)
    except Exception:
        logger.warning("Could not run domain analysis — using generic templates")

    # 3. Build procedural prompts, plan, docs using the REFINED idea + domain context
    procedural_prompts = build_prompt_pack(
        refined, flags, stack, req.target_users, req.constraints, req.industry,
        mode=mode, domain=domain, tool=tool_profile,
    )
    procedural_plan = build_implementation_plan(flags, stack, mode=mode, domain=domain, tool=tool_profile)
    procedural_docs = build_doc_pack(refined, flags, stack, req.target_users, mode=mode, domain=domain, tool=tool_profile)

    # 4. Try LLM-enriched generation
    llm_max_tokens = 2048 if mode == "mvp" else 4096

    try:
        if provider is None:
            provider = OpenAIProvider(settings.openai_api_key, settings.openai_model)
        sys_prompt = build_system_prompt(flags, stack, mode=mode)
        usr_prompt = build_user_prompt(req, flags, stack, mode=mode)
        raw = provider.generate(sys_prompt, usr_prompt, max_tokens=llm_max_tokens)
        payload = _validate_payload(_extract_json(raw))

        # Merge strategy:
        # - LLM provides implementation_plan and product_requirements (high-level analysis)
        # - Procedural templates provide all code-generation prompts (more reliable)
        merged_prompts = dict(procedural_prompts)

        llm_prompts = payload.get("prompts")
        if isinstance(llm_prompts, dict):
            pr_key = "product_requirements"
            llm_pr = llm_prompts.get(pr_key, "")
            if len(llm_pr) > len(merged_prompts.get(pr_key, "")):
                merged_prompts[pr_key] = llm_pr

        # Use LLM plan if it's good enough (MVP: 5+, production: 10+)
        min_plan_len = 5 if mode == "mvp" else 10
        llm_plan = payload.get("implementation_plan")
        final_plan = llm_plan if isinstance(llm_plan, list) and len(llm_plan) >= min_plan_len else procedural_plan

        return {
            "refined_idea": refined,
            "implementation_plan": final_plan,
            "tech_stack": stack.to_dict(),
            "prompts": merged_prompts,
            "docs": procedural_docs,
            "detected_features": sorted(flags),
            "estimated_complexity": _estimate_complexity(flags),
            "prompt_count": len(merged_prompts),
        }

    except Exception:
        logger.exception("LLM call failed — falling back to procedural generation")
        return {
            "refined_idea": refined,
            "implementation_plan": procedural_plan,
            "tech_stack": stack.to_dict(),
            "prompts": procedural_prompts,
            "docs": procedural_docs,
            "detected_features": sorted(flags),
            "estimated_complexity": _estimate_complexity(flags),
            "prompt_count": len(procedural_prompts),
        }
