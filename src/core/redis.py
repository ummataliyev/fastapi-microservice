"""
Redis configuration module.
Defines settings for connecting to a Redis database using Pydantic.
"""

from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class RedisSettings(BaseSettings):
    """
    Redis connection settings.
    """

    model_config = SettingsConfigDict(env_prefix="REDIS_")

    host: str = Field(default="redis", alias="HOST")
    port: int = Field(default=6379, alias="PORT")
    db: int = Field(default=0, alias="DB")
