import json
import logging
from typing import List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    cors_allow_origins: List[str] = ["http://localhost:3000"]
    provider: str = "openai"
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4.1"
    anthropic_api_key: Optional[str] = None

    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_jwt_secret: str = ""

    # Stripe
    stripe_secret_key: Optional[str] = None
    stripe_pro_price_id: Optional[str] = None
    stripe_enterprise_price_id: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None

    # App
    frontend_url: str = "http://localhost:3000"

    @field_validator("cors_allow_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Accept JSON array string, comma-separated string, or list."""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v = v.strip()
            # Try JSON first: '["https://example.com"]'
            if v.startswith("["):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            # Fallback: comma-separated: 'https://a.com,https://b.com'
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


settings = Settings()
logger.info("CORS allowed origins: %s", settings.cors_allow_origins)
