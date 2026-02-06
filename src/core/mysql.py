"""
MySQL configuration module.
"""

from pydantic import Field
from pydantic import computed_field

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class MySQLSettings(BaseSettings):
    """
    MySQL connection settings.
    """

    model_config = SettingsConfigDict(env_prefix="MYSQL_")

    db: str = Field(
        default="micro-service",
        validation_alias="MYSQL_DB"
    )
    user: str = Field(
        default="root",
        validation_alias="MYSQL_USER"
    )
    password: str = Field(
        default="password",
        validation_alias="MYSQL_PASSWORD"
    )
    host: str = Field(
        default="localhost",
        validation_alias="MYSQL_HOST"
    )
    port: int = Field(
        default=3306,
        validation_alias="MYSQL_PORT"
    )
    pool_size: int = Field(
        default=20,
        validation_alias="MYSQL_POOL_SIZE"
    )
    max_overflow: int = Field(
        default=10,
        validation_alias="MYSQL_MAX_OVERFLOW"
    )
    pool_timeout: int = Field(
        default=30,
        validation_alias="MYSQL_POOL_TIMEOUT"
    )
    pool_recycle: int = Field(
        default=3600,
        validation_alias="MYSQL_POOL_RECYCLE"
    )
    pool_pre_ping: bool = Field(
        default=True,
        validation_alias="MYSQL_POOL_PRE_PING"
    )
    readonly_pool_size: int = Field(
        default=5,
        validation_alias="MYSQL_READONLY_POOL_SIZE"
    )
    readonly_max_overflow: int = Field(
        default=0,
        validation_alias="MYSQL_READONLY_MAX_OVERFLOW"
    )
    readonly_pool_timeout: int = Field(
        default=30,
        validation_alias="MYSQL_READONLY_POOL_TIMEOUT"
    )
    readonly_pool_recycle: int = Field(
        default=3600,
        validation_alias="MYSQL_READONLY_POOL_RECYCLE"
    )
    readonly_pool_pre_ping: bool = Field(
        default=True,
        validation_alias="MYSQL_READONLY_POOL_PRE_PING"
    )

    @computed_field
    @property
    def url(self) -> str:
        """
        Url.

        :return: TODO - describe return value.
        :rtype: str
        :raises Exception: If the operation fails.
        """
        return f"mysql+aiomysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}" # noqa
