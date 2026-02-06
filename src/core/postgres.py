"""
PostgreSQL configuration module.
"""

from pydantic import Field
from pydantic import computed_field

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class PostgresSettings(BaseSettings):
    """
    Database connection settings for PostgreSQL.
    """

    model_config = SettingsConfigDict(env_prefix="POSTGRES_")

    db: str = Field(
        default="micro-service",
        validation_alias="POSTGRES_DB",
    )
    user: str = Field(
        default="postgres",
        validation_alias="POSTGRES_USER",
    )
    password: str = Field(
        default="password",
        validation_alias="POSTGRES_PASSWORD",
    )
    host: str = Field(
        default="localhost",
        validation_alias="POSTGRES_HOST",
    )
    port: int = Field(
        default=5432,
        validation_alias="POSTGRES_PORT",
    )
    pool_size: int = Field(
        default=20,
        validation_alias="POSTGRES_POOL_SIZE",
    )
    max_overflow: int = Field(
        default=10,
        validation_alias="POSTGRES_MAX_OVERFLOW",
    )
    pool_timeout: int = Field(
        default=30,
        validation_alias="POSTGRES_POOL_TIMEOUT",
    )
    pool_recycle: int = Field(
        default=3600,
        validation_alias="POSTGRES_POOL_RECYCLE",
    )
    pool_pre_ping: bool = Field(
        default=True,
        validation_alias="POSTGRES_POOL_PRE_PING",
    )
    readonly_pool_size: int = Field(
        default=5,
        validation_alias="POSTGRES_READONLY_POOL_SIZE",
    )
    readonly_max_overflow: int = Field(
        default=0,
        validation_alias="POSTGRES_READONLY_MAX_OVERFLOW",
    )
    readonly_pool_timeout: int = Field(
        default=30,
        validation_alias="POSTGRES_READONLY_POOL_TIMEOUT",
    )
    readonly_pool_recycle: int = Field(
        default=3600,
        validation_alias="POSTGRES_READONLY_POOL_RECYCLE",
    )
    readonly_pool_pre_ping: bool = Field(
        default=True,
        validation_alias="POSTGRES_READONLY_POOL_PRE_PING",
    )

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

    @property
    def name(self) -> str:
        """
        Backward compatibility for older call sites using `postgres.name`.
        """
        return self.db
