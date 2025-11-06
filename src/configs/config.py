"""
Configuration settings for the application.
"""

import os

from pathlib import Path

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).parent.parent


class DatabaseSettings(BaseModel):
    """
    Database connection settings for PostgreSQL.
    Reads values from environment variables with defaults.
    """

    name: str = os.getenv("POSTGRES_DB")
    user: str = os.getenv("POSTGRES_USER")
    password: str = os.getenv("POSTGRES_PASSWORD")
    host: str = os.getenv("POSTGRES_HOST")
    port: int = int(os.getenv("POSTGRES_PORT"))

    url: PostgresDsn = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"  # noqa

    @property
    def sync_url(self) -> str:
        """Return the synchronous URL for Alembic migrations."""
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    def build_url(self) -> str:
        """
        Construct the PostgreSQL DSN URL.

        :return: A PostgreSQL connection string with asyncpg driver.
        """

        return str(self.url)


class PaginationSettings(BaseModel):
    """
    Pagination-related settings.
    """

    max_entities_per_page: int = 100

    def get_max_entities(self) -> int:
        """
        Get the maximum number of entities allowed per page.

        :return: Integer representing the maximum entities per page.
        """

        return self.max_entities_per_page


class JWTSettings(BaseSettings):
    """
    Application settings with JWT configuration.
    """

    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")


class Settings(BaseSettings):
    """
    Main application settings combining all modules.
    Uses Pydantic BaseSettings to allow environment overrides.
    """

    jwt: JWTSettings = JWTSettings()
    postgres: DatabaseSettings = DatabaseSettings()
    pagination: PaginationSettings = PaginationSettings()

    model_config = ConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
