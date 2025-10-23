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


class PostgresDatabaseSettings(BaseModel):
    """
    Database connection settings for PostgreSQL.
    Reads values from environment variables with defaults.
    """

    name: str = os.getenv("POSTGRES_DB", "residential-service")
    user: str = os.getenv("POSTGRES_USER", "postgres")
    password: str = os.getenv("POSTGRES_PASSWORD", "password")
    host: str = os.getenv("POSTGRES_HOST", "localhost")
    port: int = int(os.getenv("POSTGRES_PORT", "5432"))

    url: PostgresDsn = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"  # type: ignore

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


class MinioSettings(BaseModel):
    """
    MinIO (S3-compatible storage) connection settings.
    """

    internal_endpoint: str = os.getenv("MINIO_INTERNAL_ENDPOINT", "minio:9000")
    public_endpoint: str = os.getenv("MINIO_PUBLIC_ENDPOINT", "localhost:9000")
    access_key: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    secret_key: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    bucket_name: str = os.getenv("MINIO_BUCKET_NAME", "files")
    secure: bool = os.getenv("MINIO_SECURE", "false").lower() in ["true", "1", "yes"]

    def is_secure(self) -> bool:
        return self.secure


class Settings(BaseSettings):
    """
    Main application settings combining all modules.
    Uses Pydantic BaseSettings to allow environment overrides.
    """

    pagination: PaginationSettings = PaginationSettings()
    postgres: PostgresDatabaseSettings = PostgresDatabaseSettings()
    minio: MinioSettings = MinioSettings()

    model_config = ConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
