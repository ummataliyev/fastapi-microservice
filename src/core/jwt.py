"""
JWT configuration.
Defines settings for JSON Web Tokens used in authentication.
"""

import os
import warnings

from pydantic import Field
from pydantic import model_validator
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

    @model_validator(mode="after")
    def validate_secret_key_in_production(self) -> "JWTSettings":
        """
        Warn if using default secret key in non-debug mode.
        """
        debug_mode = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
        if self.secret_key == "dev_secret_key" and not debug_mode:
            warnings.warn(
                "Using default JWT secret key in production is insecure! "
                "Set JWT_SECRET_KEY environment variable.",
                UserWarning,
                stacklevel=2,
            )
        return self
