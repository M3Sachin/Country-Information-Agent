"""
Synthesis node for Country Info Agent.
"""

import logging

from langchain_google_genai import ChatGoogleGenerativeAI

from country_info_agent.api.client import CountryAPIClient
from country_info_agent.agents.state import AgentState
from country_info_agent.config import get_settings

logger = logging.getLogger(__name__)


def synthesis_node(state: AgentState) -> AgentState:
    """
    Synthesizes the final natural language answer based on the API response.
    """
    settings = get_settings()

    if state.get("error"):
        logger.info("Synthesis node received error, providing user-friendly message")
        return {
            **state,
            "answer": f"I'm sorry, I couldn't answer that question. {state['error']}",
        }

    api_response = state.get("api_response")
    if not api_response:
        logger.warning("No api_response found in state.")
        return {
            **state,
            "answer": "I couldn't find any information about that country.",
        }

    logger.info("Synthesizing answer from API response.")

    client = CountryAPIClient()
    parsed_data = client.parse_country_data(api_response)

    if not parsed_data:
        logger.warning("Failed to parse API response")
        return {**state, "answer": "I found the country but couldn't process the data."}

    data_str = ""
    for c in parsed_data:
        data_str += f"Official Name: {c.official_name}\n"
        data_str += f"Capital: {', '.join(c.capital) if c.capital else 'N/A'}\n"
        data_str += f"Population: {c.population:,}\n"
        data_str += f"Region: {c.region}"
        if c.subregion:
            data_str += f" ({c.subregion})"
        data_str += "\n"
        data_str += f"Languages: {', '.join(c.languages.values()) if c.languages else 'N/A'}\n"
        currencies = [curr.get("name") for curr in c.currencies.values()] if c.currencies else []
        data_str += f"Currencies: {', '.join(currencies) if currencies else 'N/A'}\n"
        data_str += f"Flag: {c.flags.get('png', 'N/A')}\n"
        data_str += "---\n"

    if not settings.google_api_key:
        return {**state, "answer": _format_basic_answer(parsed_data[0])}

    try:
        llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            temperature=0.3,
            google_api_key=settings.google_api_key,
        )

        prompt = f"""You are a helpful assistant that answers questions about countries.
        Based on the following data from the REST Countries API and the original user query, provide a concise and accurate answer.

        User Query: {state["user_query"]}

        Data:
        {data_str}

        Answer the user's question directly and concisely. If multiple countries were returned (e.g., partial name match),
        mention the most relevant one or clarify. Format numbers appropriately (e.g., 83 million for population).
        """

        response = llm.invoke(prompt)

        return {**state, "answer": response.content}

    except Exception as e:
        logger.error(f"LLM synthesis failed: {e}", exc_info=True)
        return {**state, "answer": _format_basic_answer(parsed_data[0])}


def _format_basic_answer(country) -> str:
    """Format a basic answer without LLM."""
    parts = [f"The {country.name}"]

    if country.capital:
        parts.append(f"has capital {country.capital[0]}")

    parts.append(f"with population of {country.population:,}")

    if country.currencies:
        curr_names = [c.get("name") for c in country.currencies.values()]
        parts.append(f"and uses {', '.join(curr_names)} as currency")

    return ". ".join(parts) + "."
