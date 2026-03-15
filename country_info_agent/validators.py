"""
Input validation utilities for Country Info Agent.
"""

import re
from typing import Optional


class InputValidator:
    """Validates and sanitizes user input."""

    MAX_QUERY_LENGTH = 500
    MIN_QUERY_LENGTH = 3

    @staticmethod
    def validate_query(query: str) -> tuple[bool, Optional[str]]:
        """
        Validates user query.

        Returns:
            tuple: (is_valid, error_message)
        """
        if not query:
            return False, "Query cannot be empty"

        if len(query) < InputValidator.MIN_QUERY_LENGTH:
            return (
                False,
                f"Query must be at least {InputValidator.MIN_QUERY_LENGTH} characters",
            )

        if len(query) > InputValidator.MAX_QUERY_LENGTH:
            return (
                False,
                f"Query must not exceed {InputValidator.MAX_QUERY_LENGTH} characters",
            )

        return True, None

    @staticmethod
    def sanitize_country_name(name: str) -> str:
        """Sanitizes country name input."""
        if not name:
            return ""
        name = name.strip()
        name = re.sub(r"[^\w\s\-\']", "", name)
        name = re.sub(r"\s+", " ", name)
        return name[:100]

    @staticmethod
    def sanitize_query(query: str) -> str:
        """Sanitizes user query input."""
        if not query:
            return ""
        return query.strip()[: InputValidator.MAX_QUERY_LENGTH]
