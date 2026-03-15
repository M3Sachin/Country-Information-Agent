"""
LLM client using Puter's OpenAI-compatible API.
"""

import logging
from typing import Optional, List, Dict, Any

from openai import AsyncOpenAI

from country_info_agent.config import get_settings

logger = logging.getLogger(__name__)


class PuterLLMClient:
    """Client for interacting with Puter's OpenAI-compatible API."""

    BASE_URL = "https://api.puter.com/puterai/openai/v1/"

    def __init__(self):
        self.settings = get_settings()
        self._client: Optional[AsyncOpenAI] = None

    @property
    def client(self) -> AsyncOpenAI:
        """Get or create OpenAI client."""
        if self._client is None:
            self._client = AsyncOpenAI(
                base_url=self.BASE_URL,
                api_key=self.settings.puter_auth_token or "dummy",
            )
        return self._client

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.3,
    ) -> str:
        """Send a chat request and get the response."""
        model = model or self.settings.gemini_model

        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Puter API error: {e}")
            raise

    async def chat_with_structured_output(
        self,
        system_prompt: str,
        user_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0,
    ) -> Dict[str, Any]:
        """
        Send a chat request and parse JSON response.
        Used for intent extraction.
        """
        model = model or self.settings.gemini_model

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                response_format={"type": "json_object"},
            )
            import json

            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            logger.error(f"Puter API error: {e}")
            raise
