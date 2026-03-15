"""
Agent service for Country Info Agent - provides high-level interface.
"""

import logging
from typing import Optional

from country_info_agent.agents.graph import create_graph
from country_info_agent.config import get_settings
from country_info_agent.validators import InputValidator

logger = logging.getLogger(__name__)


class AgentService:
    """High-level service for Country Info Agent."""

    def __init__(self):
        self._graph = None

    @property
    def graph(self):
        """Lazy-load the graph."""
        if self._graph is None:
            self._graph = create_graph()
        return self._graph

    def health_check(self) -> dict:
        """Perform health check on the service."""
        settings = get_settings()
        health = {
            "status": "healthy",
            "api_key_configured": bool(settings.puter_auth_token),
            "config": {
                "api_timeout": settings.api_timeout,
                "max_retries": settings.max_retries,
                "log_level": settings.log_level,
            },
        }

        if not settings.puter_auth_token:
            health["status"] = "degraded"
            health["warning"] = "PUTER_AUTH_TOKEN not configured"

        return health

    def process_query(self, query: str) -> dict:
        """
        Process a single query through the agent.

        Args:
            query: User query string

        Returns:
            dict with answer or error
        """
        is_valid, error_msg = InputValidator.validate_query(query)
        if not is_valid:
            return {"answer": None, "error": error_msg}

        input_state = {
            "user_query": query,
            "country_name": None,
            "requested_fields": [],
            "api_response": None,
            "answer": None,
            "error": None,
        }

        try:
            final_state = self.graph.invoke(input_state)
            return {
                "answer": final_state.get("answer"),
                "error": final_state.get("error"),
                "country_name": final_state.get("country_name"),
                "requested_fields": final_state.get("requested_fields"),
            }
        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            return {"answer": None, "error": "An unexpected error occurred."}
