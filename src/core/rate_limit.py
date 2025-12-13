"""
Rate limiting configuration settings.
Defines limits for different HTTP methods and time windows.
"""

from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class RateLimitSettings(BaseSettings):
    """
    Rate limiting configuration for API endpoints.
    """
    model_config = SettingsConfigDict(env_prefix="RATE_LIMIT_")

    limit_get: int = Field(
        default=10,
        alias="LIMIT_GET",
        description="Max GET requests per TIME_GET"
    )
    limit_ppd: int = Field(
        default=5,
        alias="LIMIT_PPD",
        description="Max PATCH/POST/DELETE requests per TIME_PPD"
    )
    time_get: int = Field(
        default=60,
        alias="TIME_GET",
        description="Time window for GET requests in seconds"
    )
    time_ppd: int = Field(
        default=60,
        alias="TIME_PPD",
        description="Time window for PATCH/POST/DELETE requests in seconds"
    )
    rate_limit_enabled: bool = Field(
        default=True,
        alias="RATE_LIMIT_ENABLED",
        description="Enable or disable request limiting"
    )
