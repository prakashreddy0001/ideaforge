from typing import Optional

from app.providers.base import Provider


class AnthropicProvider(Provider):
    def __init__(self, api_key: Optional[str]):
        self.api_key = api_key

    def generate(self, prompt: str) -> str:
        raise NotImplementedError("Wire Anthropic SDK here.")
