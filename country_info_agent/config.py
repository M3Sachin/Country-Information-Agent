"""
Configuration management for Country Info Agent.
"""

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional

project_root = Path(__file__).parent.parent
load_dotenv(project_root / ".env")


class Settings(BaseModel):
    """Application settings with validation."""

    model_config = ConfigDict(extra="ignore")

    google_api_key: Optional[str] = Field(
        default=None, description="Google API key for LLM"
    )
    gemini_model: str = Field(
        default="gemini-2.5-flash", description="Gemini model name"
    )
    api_timeout: int = Field(default=10, description="API request timeout in seconds")
    max_retries: int = Field(
        default=3, description="Maximum number of retries for API calls"
    )
    log_level: str = Field(default="INFO", description="Logging level")
    api_base_url: str = Field(
        default="https://restcountries.com/v3.1",
        description="REST Countries API base URL",
    )
    rate_limit_delay: float = Field(
        default=0.1, description="Rate limit delay in seconds"
    )
    pool_connections: int = Field(default=10, description="HTTP pool connections")
    pool_maxsize: int = Field(default=20, description="HTTP pool max size")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            return "INFO"
        return v.upper()

    @field_validator("api_timeout")
    @classmethod
    def validate_timeout(cls, v: int) -> int:
        if v < 1:
            return 10
        if v > 60:
            return 60
        return v

    @field_validator("max_retries")
    @classmethod
    def validate_retries(cls, v: int) -> int:
        if v < 0:
            return 3
        if v > 10:
            return 10
        return v


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings(
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        api_timeout=int(os.getenv("API_TIMEOUT", "10")),
        max_retries=int(os.getenv("MAX_RETRIES", "3")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        api_base_url=os.getenv("API_BASE_URL", "https://restcountries.com/v3.1"),
        rate_limit_delay=float(os.getenv("RATE_LIMIT_DELAY", "0.1")),
        pool_connections=int(os.getenv("POOL_CONNECTIONS", "10")),
        pool_maxsize=int(os.getenv("POOL_MAXSIZE", "20")),
    )
