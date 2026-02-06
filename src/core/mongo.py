"""
MongoDB configuration module.
"""

from pydantic import Field
from pydantic import computed_field

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class MongoSettings(BaseSettings):
    """
    MongoDB connection settings.
    """

    model_config = SettingsConfigDict(env_prefix="MONGO_")

    host: str = Field(
        default="localhost",
        validation_alias="MONGO_HOST"
    )
    port: int = Field(
        default=27017,
        validation_alias="MONGO_PORT"
    )
    user: str | None = Field(
        default=None,
        validation_alias="MONGO_USER"
    )
    password: str | None = Field(
        default=None,
        validation_alias="MONGO_PASSWORD"
    )
    db: str = Field(
        default="micro-service",
        validation_alias="MONGO_DB"
    )

    @computed_field
    @property
    def uri(self) -> str:
        """
        Uri.

        :return: TODO - describe return value.
        :rtype: str
        :raises Exception: If the operation fails.
        """
        if self.user and self.password:
            return f"mongodb://{self.user}:{self.password}@{self.host}:{self.port}" # noqa

        return f"mongodb://{self.host}:{self.port}"
