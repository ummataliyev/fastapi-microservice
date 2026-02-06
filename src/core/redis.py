"""
Redis configuration module.
"""

from pydantic import Field

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class RedisSettings(BaseSettings):
    """
    Redis connection settings.
    """

    model_config = SettingsConfigDict(env_prefix="REDIS_")

    host: str = Field(
        default="localhost",
        validation_alias="REDIS_HOST",
    )
    port: int = Field(
        default=6379,
        validation_alias="REDIS_PORT",
    )
    db: int = Field(
        default=0,
        validation_alias="REDIS_DB",
    )
    socket_connect_timeout: float = Field(
        default=2.0,
        validation_alias="REDIS_SOCKET_CONNECT_TIMEOUT",
    )
    socket_timeout: float = Field(
        default=2.0,
        validation_alias="REDIS_SOCKET_TIMEOUT",
    )
    health_check_interval: int = Field(
        default=30,
        validation_alias="REDIS_HEALTH_CHECK_INTERVAL",
    )
    retry_on_timeout: bool = Field(
        default=True,
        validation_alias="REDIS_RETRY_ON_TIMEOUT",
    )
