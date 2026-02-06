"""
Application settings module.
"""

import json

from typing import Any
from typing import Annotated

from pydantic import Field
from pydantic import field_validator
from pydantic import model_validator

from pydantic_settings import NoDecode
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

from src.core.jwt import JWTSettings
from src.core.redis import RedisSettings
from src.core.mongo import MongoSettings
from src.core.mysql import MySQLSettings
from src.core.postgres import PostgresSettings
from src.core.rate_limit import RateLimitSettings
from src.core.pagination import PaginationSettings
from src.core.http_client import HTTPClientSettings


class Settings(BaseSettings):
    """
    Settings class.
    :raises Exception: If class initialization or usage fails.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    app_name: str = Field(default="FastAPI Microservice", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    app_env: str = Field(default="development", alias="APP_ENV")
    db_provider: str = Field(default="postgres", alias="DB_PROVIDER")
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")
    debug: bool = Field(default=False, alias="DEBUG")
    tracing_enabled: bool = Field(default=False, alias="TRACING_ENABLED")
    docs_enabled: bool = Field(default=True, alias="DOCS_ENABLED")
    redoc_enabled: bool = Field(default=True, alias="REDOC_ENABLED")
    openapi_enabled: bool = Field(default=True, alias="OPENAPI_ENABLED")
    run_migrations_on_start: bool = Field(default=True, alias="RUN_MIGRATIONS_ON_START")
    auth_login_max_attempts: int = Field(default=5, alias="AUTH_LOGIN_MAX_ATTEMPTS")
    auth_login_window_seconds: int = Field(default=300, alias="AUTH_LOGIN_WINDOW_SECONDS")
    auth_login_lockout_seconds: int = Field(default=900, alias="AUTH_LOGIN_LOCKOUT_SECONDS")

    allowed_origins: Annotated[list[str], NoDecode] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        alias="ALLOWED_ORIGINS",
    )
    trusted_hosts: Annotated[list[str], NoDecode] = Field(default=["*"], alias="TRUSTED_HOSTS")
    slow_request_threshold_ms: float = Field(
        default=1000.0, alias="SLOW_REQUEST_THRESHOLD_MS"
    )

    jwt: JWTSettings = JWTSettings()
    redis: RedisSettings = RedisSettings()
    mysql: MySQLSettings = MySQLSettings()
    mongo: MongoSettings = MongoSettings()
    postgres: PostgresSettings = PostgresSettings()
    rate_limit: RateLimitSettings = RateLimitSettings()
    http_client: HTTPClientSettings = HTTPClientSettings()
    pagination: PaginationSettings = PaginationSettings()

    @field_validator("allowed_origins", "trusted_hosts", mode="before")
    @classmethod
    def parse_csv_list(cls, value: Any) -> list[str] | Any:
        """
        Parse csv list.

        :param value: TODO - describe value.
        :type value: Any
        :return: TODO - describe return value.
        :rtype: list[str] | Any
        :raises Exception: If the operation fails.
        """
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("["):
                try:
                    parsed = json.loads(stripped)
                    if isinstance(parsed, list):
                        return [str(item).strip() for item in parsed if str(item).strip()]
                except json.JSONDecodeError:
                    pass
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @model_validator(mode="after")
    def validate_env_security_defaults(self) -> "Settings":
        """
        Validate env security defaults.

        :return: TODO - describe return value.
        :rtype: 'Settings'
        :raises ValueError: If the operation cannot be completed.
        """
        env = self.app_env.lower()
        if env not in {"development", "dev", "local", "test", "staging", "production", "prod"}:
            raise ValueError(
                "APP_ENV must be one of: development, dev, local, test, staging, production, prod"
            )
        provider = self.db_provider.lower()
        if provider not in {"postgres", "mysql", "mongo"}:
            raise ValueError("DB_PROVIDER must be one of: postgres, mysql, mongo")

        is_dev_like = env in {"development", "dev", "local", "test"}
        if "*" in self.trusted_hosts and not is_dev_like:
            raise ValueError("TRUSTED_HOSTS='*' is not allowed outside development/test environments")

        return self


settings = Settings()
