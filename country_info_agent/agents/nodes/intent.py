"""
Intent extraction node for Country Info Agent.
"""

import logging

from langchain_google_genai import ChatGoogleGenerativeAI

from country_info_agent.agents.state import AgentState, ExtractionOutput
from country_info_agent.config import get_settings
from country_info_agent.validators import InputValidator

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

    if not settings.google_api_key:
        logger.error("Google API key not configured")
        return {
            **state,
            "error": "Service configuration error. Please contact support.",
        }

    try:
        llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            temperature=0,
            google_api_key=settings.google_api_key,
        )
        structured_llm = llm.with_structured_output(ExtractionOutput)

        prompt = f"""Extract the country name and the specific information requested from the user's question.
        User Question: {sanitized_query}

        Return a valid JSON with:
        - country_name: The name of the country
        - fields: List of information requested (e.g., population, capital, currency, language, area, region)
        """

        output = structured_llm.invoke(prompt)

        if not output or not output.country_name:
            logger.warning("Failed to extract country name from query")
            return {**state, "error": "Could not identify a country in your query."}

        logger.info(f"Extracted country: {output.country_name}, fields: {output.fields}")

        return {
            **state,
            "country_name": output.country_name,
            "requested_fields": output.fields,
        }

    except Exception as e:
        logger.error(f"Intent extraction node failed: {e}", exc_info=True)
        return {**state, "error": "Failed to process your request. Please try again."}
