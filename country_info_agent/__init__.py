"""
Country Info Agent - An AI agent that answers questions about countries using REST Countries API.
"""

__version__ = "1.0.0"

from country_info_agent.api.client import CountryAPIClient, CountryInfo
from country_info_agent.api.exceptions import CountryAPIError, CountryNotFoundError
from country_info_agent.agents.state import AgentState
from country_info_agent.agents.graph import create_graph
from country_info_agent.config import get_settings

__all__ = [
    "CountryAPIClient",
    "CountryInfo",
    "CountryAPIError",
    "CountryNotFoundError",
    "AgentState",
    "create_graph",
    "get_settings",
]
