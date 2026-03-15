"""
LLM client using Puter's OpenAI-compatible API.
"""

import logging
import json
import re
from typing import Optional, List, Dict, Any

from openai import OpenAI

from country_info_agent.config import get_settings

logger = logging.getLogger(__name__)


class PuterLLMClient:
    """Client for interacting with Puter's OpenAI-compatible API."""

    BASE_URL = "https://api.puter.com/puterai/openai/v1/"

    def __init__(self):
        self.settings = get_settings()
        self._client: Optional[OpenAI] = None

    @property
    def client(self) -> OpenAI:
        """Get or create OpenAI client."""
        if self._client is None:
            self._client = OpenAI(
                base_url=self.BASE_URL,
                api_key=self.settings.puter_auth_token or "dummy",
            )
        return self._client

    def _clean_json_response(self, content: str) -> str:
        """Clean markdown code blocks from JSON response."""
        content = content.strip()
        # Remove markdown code blocks
        content = re.sub(r"^```json\s*", "", content)
        content = re.sub(r"^```\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
        return content

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.3,
    ) -> str:
        """Send a chat request and get the response."""
        model = model or self.settings.gemini_model

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
            )
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from Puter API")
            return content
        except Exception as e:
            logger.error(f"Puter API error: {e}")
            raise

    def chat_with_structured_output(
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
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content

            if not content:
                raise ValueError("Empty response from Puter API")

            # Clean markdown code blocks
            content = self._clean_json_response(content)

            return json.loads(content)
        except Exception as e:
            logger.error(f"Puter API error: {e}")
            raise
