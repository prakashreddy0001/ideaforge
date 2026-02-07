from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    cors_allow_origins: List[str] = ["http://localhost:3000"]
    provider: str = "openai"
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4.1"
    anthropic_api_key: Optional[str] = None


settings = Settings()
