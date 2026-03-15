"""
Custom exceptions for the Country Info Agent API.
"""


class CountryAPIError(Exception):
    """Base exception for Country API errors."""

    pass


class CountryNotFoundError(CountryAPIError):
    """Raised when a country is not found."""

    pass


class RateLimitError(CountryAPIError):
    """Raised when rate limit is exceeded."""

    pass


class TimeoutError(CountryAPIError):
    """Raised when API request times out."""

    pass
