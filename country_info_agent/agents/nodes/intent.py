"""
Intent extraction node for Country Info Agent.
"""

import logging

from country_info_agent.agents.state import AgentState
from country_info_agent.config import get_settings
from country_info_agent.validators import InputValidator
from country_info_agent.api.llm_client import PuterLLMClient

logger = logging.getLogger(__name__)


def intent_node(state: AgentState) -> AgentState:
    """
    Identifies the country and requested fields from the user query.
    Performs input validation and error handling.
    """
    settings = get_settings()

    query = state.get("user_query", "")
    logger.info(f"Processing query: {query}")

    is_valid, error_msg = InputValidator.validate_query(query)
    if not is_valid:
        logger.warning(f"Invalid query: {error_msg}")
        return {**state, "error": error_msg}

    sanitized_query = InputValidator.sanitize_query(query)

    if not settings.puter_auth_token:
        logger.error("Puter auth token not configured")
        return {
            **state,
            "error": "Service not configured. Please set PUTER_AUTH_TOKEN.",
        }

    try:
        client = PuterLLMClient()

        prompt = f"""Extract the country name and the specific information requested from the user's question.
User Question: {sanitized_query}

Return a valid JSON with:
- country_name: The name of the country
- fields: List of information requested (e.g., population, capital, currency, language, area, region)"""

        result = client.chat_with_structured_output(
            system_prompt="You are a helpful assistant that extracts information from user queries. Always respond with valid JSON.",
            user_prompt=prompt,
            model=settings.gemini_model,
            temperature=0,
        )

        country_name = result.get("country_name", "").strip()
        fields = result.get("fields", [])

        if not country_name:
            logger.warning("Failed to extract country name from query")
            return {**state, "error": "Could not identify a country in your query."}

        logger.info(f"Extracted country: {country_name}, fields: {fields}")

        return {
            **state,
            "country_name": country_name,
            "requested_fields": fields,
        }

    except Exception as e:
        logger.error(f"Intent extraction node failed: {e}", exc_info=True)
        return {**state, "error": "Failed to process your request. Please try again."}
