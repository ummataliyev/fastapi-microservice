from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.jwt import JWTSettings
from src.core.postgres import PostgresSettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    app_name: str = "Template Service"
    app_version: str = "0.1.0"
    app_env: str = "development"
    log_level: str = "INFO"
    sentry_dsn: str = ""

    # CORS — comma-separated origins, e.g. "https://app.safiabakery.uz,https://admin.safiabakery.uz"
    # Use ["*"] for permissive dev only.
    cors_allow_origins: list[str] = ["*"]

    slow_request_threshold_ms: float = 1000.0

    docs_username: str = "admin"
    docs_password: str = "admin"

    permission_service_url: str = ""
    permission_service_token: str = ""

    postgres: PostgresSettings = PostgresSettings()
    jwt: JWTSettings = JWTSettings()

    @property
    def database_url(self) -> str:
        return self.postgres.url

    @property
    def jwt_secret_key(self) -> str:
        return self.jwt.secret_key

    @property
    def access_token_expire_minutes(self) -> int:
        return self.jwt.access_token_expire_minutes


settings = Settings()
