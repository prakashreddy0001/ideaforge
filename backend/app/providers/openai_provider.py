from typing import Optional

from openai import OpenAI


class OpenAIProvider:
    def __init__(self, api_key: Optional[str], model: str):
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set.")
        self.client = OpenAI(api_key=api_key, timeout=60.0)
        self.model = model

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content or ""

    def generate_with_vision(
        self,
        system_prompt: str,
        user_content: list,
        max_tokens: int = 8192,
        temperature: float = 0.3,
    ) -> str:
        """Generate a response from an image + text prompt (Vision API).

        Unlike generate(), this does NOT use response_format=json_object
        because vision requests return raw code/text, not structured JSON.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=120.0,
        )
        return response.choices[0].message.content or ""


_shared_provider: Optional[OpenAIProvider] = None


def get_provider() -> OpenAIProvider:
    """Return a shared OpenAIProvider singleton (reuses HTTP connection pool)."""
    global _shared_provider
    if _shared_provider is None:
        from app.core.config import settings
        _shared_provider = OpenAIProvider(settings.openai_api_key, settings.openai_model)
    return _shared_provider
