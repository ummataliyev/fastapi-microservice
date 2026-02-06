"""
HTTP client configuration module.
"""

from pydantic import Field
from pydantic import field_validator

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class HTTPClientSettings(BaseSettings):
    """
    HTTP client configuration for outgoing service calls.
    """

    model_config = SettingsConfigDict(env_prefix="HTTP_CLIENT_")

    timeout: float = Field(
        default=10.0,
        gt=0,
        alias="HTTP_CLIENT_TIMEOUT"
    )
    connect_timeout: float = Field(
        default=2.0,
        gt=0,
        alias="HTTP_CLIENT_CONNECT_TIMEOUT"
    )
    retries: int = Field(
        default=2,
        ge=0,
        le=10,
        alias="HTTP_CLIENT_RETRIES"
    )
    pool_connections: int = Field(
        default=10,
        ge=1,
        alias="HTTP_CLIENT_POOL_CONNECTIONS"
    )
    pool_maxsize: int = Field(
        default=20,
        ge=1,
        alias="HTTP_CLIENT_POOL_MAXSIZE"
    )

    @field_validator("connect_timeout")
    @classmethod
    def validate_connect_timeout(cls, v: float, info) -> float:
        """
        Validate connect timeout.

        :param v: TODO - describe v.
        :type v: float
        :param info: TODO - describe info.
        :return: TODO - describe return value.
        :rtype: float
        :raises ValueError: If the operation cannot be completed.
        """
        if "timeout" in info.data and v > info.data["timeout"]:
            raise ValueError("connect_timeout cannot exceed timeout")
        return v
