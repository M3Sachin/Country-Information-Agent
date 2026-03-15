"""
Tool invocation node for Country Info Agent.
"""

import logging

from country_info_agent.api.client import CountryAPIClient
from country_info_agent.api.exceptions import CountryAPIError
from country_info_agent.agents.state import AgentState
from country_info_agent.validators import InputValidator

logger = logging.getLogger(__name__)


def tool_invocation_node(state: AgentState) -> AgentState:
    """
    Invokes the REST Countries API based on the extracted country name.
    """
    if state.get("error"):
        return state

    country_name = state.get("country_name")
    if not country_name:
        logger.error("No country name extracted in tool node.")
        return {**state, "error": "No country name extracted."}

    sanitized_name = InputValidator.sanitize_country_name(country_name)
    if not sanitized_name:
        logger.warning(f"Invalid country name after sanitization: {country_name}")
        return {**state, "error": "Invalid country name."}

    logger.info(f"Fetching data for country: {sanitized_name}")

    try:
        client = CountryAPIClient()
        response = client.get_country_info(sanitized_name)

        if response is None:
            logger.warning(f"Country '{sanitized_name}' not found.")
            return {**state, "error": f"Country '{sanitized_name}' not found."}

        logger.info(f"Successfully retrieved data for {sanitized_name}")

        return {**state, "api_response": response}

    except CountryAPIError as e:
        logger.error(f"API error: {e}", exc_info=True)
        return {**state, "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error in tool invocation: {e}", exc_info=True)
        return {**state, "error": "Failed to fetch country data. Please try again."}
