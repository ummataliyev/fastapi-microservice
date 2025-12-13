"""
Configuration settings for the application.
"""

from pathlib import Path
from pydantic import Field
from pydantic import computed_field
from pydantic import field_validator
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


BASE_DIR = Path(__file__).parent.parent


class DatabaseSettings(BaseSettings):
    """
    Database connection settings for PostgreSQL.
    """

    model_config = SettingsConfigDict(env_prefix="POSTGRES_")

    db: str = Field(default="micro-service", alias="DB")
    user: str = Field(default="postgres", alias="USER")
    password: str = Field(default="password", alias="PASSWORD")
    host: str = Field(default="service-db", alias="HOST")
    port: int = Field(default=5432, alias="PORT")

    @computed_field
    @property
    def url(self) -> str:
        """
        Construct PostgreSQL DSN for asyncpg.
        """
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}" # noqa
        )

    def build_url(self) -> str:
        """
        Backward compatibility for Alembic.
        """
        return self.url


class RedisSettings(BaseSettings):
    """
    Redis connection settings.
    """

    model_config = SettingsConfigDict(env_prefix="REDIS_")

    host: str = Field(default="redis", alias="HOST")
    port: int = Field(default=6379, alias="PORT")
    db: int = Field(default=0, alias="DB")


class PaginationSettings(BaseSettings):
    """
    Pagination-related configuration.
    """

    model_config = SettingsConfigDict()

    max_entities_per_page: int = Field(
        default=100,
        ge=1,
        le=1000,
        alias="MAX_ENTITIES_PER_PAGE",
        description="Maximum number of entities per page",
    )


class JWTSettings(BaseSettings):
    """
    JWT configuration.
    """

    model_config = SettingsConfigDict(env_prefix="JWT_")

    secret_key: str = Field("dev_secret_key", alias="SECRET_KEY")
    algorithm: str = Field("HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(30, alias="ACCESS_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(7, alias="REFRESH_EXPIRE_DAYS")


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
        if "timeout" in info.data and v > info.data["timeout"]:
            raise ValueError("connect_timeout cannot exceed timeout")
        return v


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


class Settings(BaseSettings):
    """
    Root application settings.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    jwt: JWTSettings = JWTSettings()
    redis: RedisSettings = RedisSettings()
    postgres: DatabaseSettings = DatabaseSettings()
    rate_limit: RateLimitSettings = RateLimitSettings()
    pagination: PaginationSettings = PaginationSettings()
    http_client: HTTPClientSettings = HTTPClientSettings()


settings = Settings()
