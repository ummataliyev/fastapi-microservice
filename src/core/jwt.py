"""
JWT configuration.
Defines settings for JSON Web Tokens used in authentication.
"""

from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class JWTSettings(BaseSettings):
    """
    JWT configuration.
    """

    model_config = SettingsConfigDict(env_prefix="JWT_")

    secret_key: str = Field("dev_secret_key", alias="SECRET_KEY")
    algorithm: str = Field("HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(30, alias="ACCESS_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(7, alias="REFRESH_EXPIRE_DAYS")
