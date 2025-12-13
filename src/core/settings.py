"""
Application settings module.
Defines configuration settings for the application using Pydantic.
"""

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

from src.core.jwt import JWTSettings
from src.core.redis import RedisSettings
from src.core.database import DatabaseSettings
from src.core.rate_limit import RateLimitSettings
from src.core.pagination import PaginationSettings
from src.core.http_client import HTTPClientSettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    jwt: JWTSettings = JWTSettings()
    redis: RedisSettings = RedisSettings()
    postgres: DatabaseSettings = DatabaseSettings()
    rate_limit: RateLimitSettings = RateLimitSettings()
    http_client: HTTPClientSettings = HTTPClientSettings()
    pagination: PaginationSettings = PaginationSettings()


settings = Settings()
