"""
Database configuration module.
Defines settings for connecting to a PostgreSQL database using Pydantic.
"""

from pydantic import Field
from pydantic import computed_field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


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
