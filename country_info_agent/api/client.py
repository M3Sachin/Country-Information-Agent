"""
Client for fetching country information from REST Countries API.
"""

import logging
import time
from typing import Optional, Dict, Any, List

import requests
from pydantic import BaseModel, Field
from requests.adapters import HTTPAdapter

from country_info_agent.api.exceptions import CountryAPIError
from country_info_agent.config import get_settings

logger = logging.getLogger(__name__)


class CountryInfo(BaseModel):
    """Model for country information."""

    name: str
    official_name: str
    capital: List[str] = Field(default_factory=list)
    region: str
    subregion: Optional[str] = None
    population: int
    languages: Dict[str, str] = Field(default_factory=dict)
    currencies: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    flags: Dict[str, str] = Field(default_factory=dict)


class CountryAPIClient:
    """Client for fetching country information from REST Countries API."""

    def __init__(self):
        self.settings = get_settings()
        self._session = None
        self._last_request_time = 0

    @property
    def session(self) -> requests.Session:
        """Get or create a requests session."""
        if self._session is None:
            self._session = requests.Session()
            adapter = HTTPAdapter(
                max_retries=self.settings.max_retries,
                pool_connections=self.settings.pool_connections,
                pool_maxsize=self.settings.pool_maxsize,
            )
            self._session.mount("http://", adapter)
            self._session.mount("https://", adapter)
        return self._session

    def _rate_limit(self):
        """Apply simple rate limiting."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.settings.rate_limit_delay:
            time.sleep(self.settings.rate_limit_delay - elapsed)
        self._last_request_time = time.time()

    def get_country_info(self, country_name: str) -> Optional[List[Dict[str, Any]]]:
        """
        Fetches country information from the REST Countries API with retry logic.

        Args:
            country_name: Name of the country to search for.

        Returns:
            List of country data or None if not found.

        Raises:
            CountryAPIError: If API request fails after retries.
        """
        self._rate_limit()

        for attempt in range(self.settings.max_retries):
            try:
                logger.debug(
                    f"Fetching country info for: {country_name} (attempt {attempt + 1})"
                )

                response = self.session.get(
                    f"{self.settings.api_base_url}/name/{country_name}",
                    timeout=self.settings.api_timeout,
                )

                if response.status_code == 404:
                    logger.info(f"Country not found: {country_name}")
                    return None

                if response.status_code == 429:
                    wait_time = 2**attempt
                    logger.warning(f"Rate limited, waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue

                response.raise_for_status()
                data = response.json()

                if not data:
                    logger.warning(f"Empty response for country: {country_name}")
                    return None

                logger.info(f"Successfully fetched data for: {country_name}")
                return data

            except requests.Timeout:
                logger.warning(
                    f"Request timeout for {country_name} (attempt {attempt + 1})"
                )
                if attempt == self.settings.max_retries - 1:
                    raise CountryAPIError("Request timed out. Please try again.")

            except requests.RequestException as e:
                logger.warning(
                    f"Request error for {country_name}: {e} (attempt {attempt + 1})"
                )
                if attempt == self.settings.max_retries - 1:
                    raise CountryAPIError(f"Failed to fetch country data: {str(e)}")

        return None

    def parse_country_data(self, data: List[Dict[str, Any]]) -> List[CountryInfo]:
        """
        Parses raw API data into CountryInfo models.
        """
        countries = []
        for item in data:
            countries.append(
                CountryInfo(
                    name=item.get("name", {}).get("common", "Unknown"),
                    official_name=item.get("name", {}).get("official", "Unknown"),
                    capital=item.get("capital", []),
                    region=item.get("region", "Unknown"),
                    subregion=item.get("subregion"),
                    population=item.get("population", 0),
                    languages=item.get("languages", {}),
                    currencies=item.get("currencies", {}),
                    flags=item.get("flags", {}),
                )
            )
        return countries
