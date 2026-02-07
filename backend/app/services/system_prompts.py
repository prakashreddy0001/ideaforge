"""Enhanced LLM system and user prompt construction.

These prompts are sent to the AI provider (OpenAI) to generate the
high-level product analysis and implementation plan.  The heavy code-generation
prompts are built procedurally in ``prompt_templates.py`` — this module only
handles the LLM conversation.
"""

from typing import List, Optional, Set

from app.api.schemas import IdeaRequest
from app.services.feature_detection import FEATURE_DESCRIPTIONS
from app.services.stack_selection import StackChoice


def _mvp_system_prompt() -> str:
    return (
        "You are a senior engineer helping plan an MVP. "
        "Return ONLY valid JSON (no markdown fences) with these keys:\n"
        '  "implementation_plan": array of 6-8 short steps to build an MVP fast,\n'
        '  "tech_stack": object of technology choices,\n'
        '  "prompts": {"product_requirements": "a concise 800-1200 char product brief"},\n'
        '  "docs": {"readme": "a short 500 char project readme"}.\n'
        "Focus on speed to market, not perfection. Keep everything lean."
    )


def _mvp_user_prompt(req: "IdeaRequest") -> str:
    parts = [f"## Idea\n{req.idea}"]
    if req.target_users:
        parts.append(f"## Target Users\n{req.target_users}")
    if req.budget:
        parts.append(f"## Budget\n{req.budget}")
    parts.append(
        "## Goal\nProduce a lean MVP plan. Prioritise the single most important "
        "workflow. Skip advanced features, monitoring, and security hardening."
    )
    return "\n\n".join(parts)


def build_system_prompt(flags: Set[str], stack: StackChoice, mode: str = "production") -> str:
    """Construct the system prompt for the LLM."""
    if mode == "mvp":
        return _mvp_system_prompt()

    stack_lines = "\n".join(
        f"  - {k.replace('_', ' ').title()}: {v}"
        for k, v in stack.to_dict().items()
        if v != "None"
    )

    feature_lines = ""
    if flags:
        feature_lines = "\n".join(
            f"  - {f}: {FEATURE_DESCRIPTIONS.get(f, f)}"
            for f in sorted(flags)
        )
        feature_lines = f"""
The following feature capabilities were detected in the idea:
{feature_lines}
Incorporate ALL of these into your response — do not ignore any detected feature.
"""

    return f"""You are a principal full-stack engineer and system architect with 15+ years of
experience shipping production SaaS applications. You have deep expertise in
product strategy, system design, database modelling, API design, security,
DevOps, and frontend architecture.

Your task is to analyse a product idea and produce a DEEPLY DETAILED implementation
package as valid JSON. Your output will be used by a development team to build
the application from scratch.

## Chosen Tech Stack
{stack_lines}
{feature_lines}
## Output Format — STRICT JSON

Return ONLY valid JSON (no markdown fences, no commentary) with these exact keys:

{{
  "implementation_plan": [
    // Array of 15-25 strings. Each string is a granular, actionable step
    // organised in phases: Foundation → Backend → Frontend → Features → Launch.
    // Reference specific technologies from the stack above.
    // Each step should be 1-2 sentences with enough detail to act on.
  ],
  "tech_stack": {{
    // Object mirroring the stack above. You may refine or add justifications.
    // Keys: frontend, frontend_ui, backend, database, cache, infra, auth, ai,
    //        search, file_storage, email, monitoring, testing
  }},
  "prompts": {{
    "product_requirements": "...",
    // A 2000+ character comprehensive Product Requirements Document including:
    // problem statement, 3+ user personas, 15+ user stories (Given/When/Then),
    // MVP feature prioritisation (P0/P1/P2), acceptance criteria, NFRs,
    // success metrics with targets, risks, and out-of-scope items.
  }},
  "docs": {{
    "readme": "...",
    // A 1500+ character project README with architecture diagram, setup
    // instructions, environment variables, project structure, and scripts.
  }}
}}

## Quality Gates
- The product_requirements prompt MUST be at least 2000 characters.
- The readme doc MUST be at least 1500 characters.
- Every implementation step MUST reference a specific technology or tool.
- Do NOT use vague phrases like "implement as needed" or "add relevant features".
- Do NOT add markdown code fences around the JSON.
- Do NOT include any text outside the JSON object.
"""


def build_user_prompt(
    req: IdeaRequest,
    flags: Set[str],
    stack: StackChoice,
    mode: str = "production",
) -> str:
    """Construct the user prompt for the LLM."""
    if mode == "mvp":
        return _mvp_user_prompt(req)

    sections: List[str] = []

    # Core idea
    sections.append(f"## Product Idea\n{req.idea}")

    # Target users
    if req.target_users:
        sections.append(f"## Target Users\n{req.target_users}")

    # Budget / timeline
    if req.budget:
        sections.append(f"## Budget\n{req.budget}")
    if req.timeline:
        sections.append(f"## Timeline\n{req.timeline}")

    # Constraints
    if req.constraints:
        items = "\n".join(f"- {c}" for c in req.constraints)
        sections.append(f"## Constraints\n{items}")

    # Industry compliance
    if req.industry:
        sections.append(
            f"## Industry\n{req.industry}\n"
            "Consider relevant compliance requirements (HIPAA, PCI-DSS, GDPR, SOC 2, etc.)."
        )

    # Preferred stack hints
    if req.preferred_stack:
        sections.append(
            f"## User's Stack Preferences\n{req.preferred_stack}\n"
            "Incorporate these preferences where they don't conflict with detected requirements."
        )

    # Detected features
    if flags:
        feature_list = "\n".join(
            f"- **{f}**: {FEATURE_DESCRIPTIONS.get(f, f)}"
            for f in sorted(flags)
        )
        sections.append(f"## Detected Features\n{feature_list}")

    # Stack summary
    stack_summary = "\n".join(
        f"- {k.replace('_', ' ').title()}: {v}"
        for k, v in stack.to_dict().items()
        if v != "None"
    )
    sections.append(f"## Selected Tech Stack\n{stack_summary}")

    # Scope guidance
    if req.budget:
        budget_lower = req.budget.lower()
        if any(w in budget_lower for w in ["small", "low", "minimal", "bootstrap", "< 5k", "<5k"]):
            sections.append(
                "## Scope Guidance\nBudget is limited — focus on a lean MVP. "
                "Minimise paid services, prefer open-source alternatives, and defer non-essential features."
            )
        elif any(w in budget_lower for w in ["large", "high", "enterprise", "> 50k", ">50k"]):
            sections.append(
                "## Scope Guidance\nBudget is substantial — plan for production-grade infrastructure, "
                "comprehensive monitoring, and polished UX from day one."
            )

    # Deliverables reminder
    sections.append(
        "## Expected Deliverables\n"
        "Return a JSON object with keys: implementation_plan, tech_stack, prompts, docs.\n"
        "- implementation_plan: 15-25 granular steps in phases\n"
        "- tech_stack: full technology choices\n"
        "- prompts.product_requirements: 2000+ character PRD\n"
        "- docs.readme: 1500+ character project README"
    )

    return "\n\n".join(sections)
