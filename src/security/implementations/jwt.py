from datetime import datetime, timedelta, timezone

import jwt

from src.core.settings import settings
from src.exceptions.services.base import UnauthorizedError


class PyJWTHandler:
    def __init__(
        self,
        secret_key: str | None = None,
        algorithm: str | None = None,
        default_expire_minutes: int | None = None,
    ) -> None:
        self.secret_key = secret_key or settings.jwt.secret_key
        self.algorithm = algorithm or settings.jwt.algorithm
        self.default_expire_minutes = (
            default_expire_minutes
            if default_expire_minutes is not None
            else settings.jwt.access_token_expire_minutes
        )

    def encode(self, payload: dict, expires_delta_minutes: int | None = None) -> str:
        to_encode = payload.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=expires_delta_minutes or self.default_expire_minutes
        )
        to_encode["exp"] = expire
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def decode(self, token: str) -> dict:
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError as exc:
            raise UnauthorizedError("Token expired") from exc
        except jwt.InvalidTokenError as exc:
            raise UnauthorizedError("Invalid token") from exc


jwt_handler = PyJWTHandler()
