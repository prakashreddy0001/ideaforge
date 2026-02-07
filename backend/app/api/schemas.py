from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class IdeaRequest(BaseModel):
    idea: str = Field(..., min_length=10, max_length=4000)
    constraints: List[str] = []
    target_users: Optional[str] = None
    budget: Optional[str] = None
    preferred_stack: Optional[str] = None
    industry: Optional[str] = None
    timeline: Optional[str] = None
    mode: str = "production"  # "mvp" or "production"
    tool: Optional[str] = None  # "lovable", "replit", "base44", "claude_code", or None


class IdeaResponse(BaseModel):
    implementation_plan: List[str]
    tech_stack: Dict[str, str]
    prompts: Dict[str, str]
    docs: Dict[str, str]
    refined_idea: Optional[str] = None
    detected_features: Optional[List[str]] = None
    estimated_complexity: Optional[str] = None
    prompt_count: Optional[int] = None
