"""
Agent state definitions for Country Info Agent.
"""

from typing import TypedDict, List, Optional, Dict, Any

from pydantic import BaseModel, Field, field_validator

from country_info_agent.validators import InputValidator


class AgentState(TypedDict):
    """State of the agent at any given point."""

    user_query: str
    country_name: Optional[str]
    requested_fields: List[str]
    api_response: Optional[List[Dict[str, Any]]]
    answer: Optional[str]
    error: Optional[str]


class ExtractionOutput(BaseModel):
    """Output from the intent extraction node."""

    country_name: str = Field(
        description="The name of the country identified in the query."
    )
    fields: List[str] = Field(
        description="The specific information requested about the country."
    )

    @field_validator("country_name")
    @classmethod
    def validate_country_name(cls, v: str) -> str:
        """Validate and sanitize country name."""
        return InputValidator.sanitize_country_name(v)
