from typing import Optional

from openai import OpenAI


class OpenAIProvider:
    def __init__(self, api_key: Optional[str], model: str):
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set.")
        self.client = OpenAI(api_key=api_key)
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
