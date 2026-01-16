"""
JWT Token Service Implementation using PyJWT.
"""

import jwt

from typing import Any
from typing import Dict

from datetime import datetime
from datetime import timedelta
from datetime import timezone

from jwt import ExpiredSignatureError
from jwt import InvalidTokenError as PyJWTInvalidTokenError

from src.security.interfaces.token import TokenService
from src.security.exceptions.token import TokenError
from src.security.exceptions.token import TokenExpiredError
from src.security.exceptions.token import InvalidTokenError

from src.core.config import settings


class JWTTokenService(TokenService):
    """
    PyJWT-based implementation of TokenService using HS algorithms.

    Provides methods to create and decode JWT access and refresh tokens.
    """

    def __init__(
        self,
        secret_key: str = settings.jwt.secret_key,
        algorithm: str = settings.jwt.algorithm,
        access_exp_minutes: int = settings.jwt.access_token_expire_minutes,
        refresh_exp_days: int = settings.jwt.refresh_token_expire_days,
    ):
        """
        Initialize the JWTTokenService.

        :param secret_key: Secret key used for encoding and decoding tokens.
        :param algorithm: Algorithm to use for JWT encoding/decoding (e.g., HS256).
        :param access_exp_minutes: Expiration time for access tokens in minutes.
        :param refresh_exp_days: Expiration time for refresh tokens in days.
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_exp_minutes = access_exp_minutes
        self.refresh_exp_days = refresh_exp_days

    def _encode(self, data: Dict[str, Any], exp: datetime, token_type: str) -> str:
        """
        Encode a JWT token with the given payload and expiration.

        :param data: Dictionary of claims to include in the token.
        :param exp: Expiration datetime for the token.
        :param token_type: Type of the token ("access" or "refresh").
        :return: Encoded JWT token as a string.
        """
        payload = data.copy()
        payload.update({"exp": exp, "type": token_type})

        return jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm,
        )

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """
        Create a JWT access token.

        :param data: Dictionary of claims to include in the token.
        :return: Encoded JWT access token as a string.
        """
        exp = datetime.now(timezone.utc) + timedelta(minutes=self.access_exp_minutes)
        return self._encode(data, exp, "access")

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """
        Create a JWT refresh token.

        :param data: Dictionary of claims to include in the token.
        :return: Encoded JWT refresh token as a string.
        """
        exp = datetime.now(timezone.utc) + timedelta(days=self.refresh_exp_days)
        return self._encode(data, exp, "refresh")

    def decode(self, token: str) -> Dict[str, Any]:
        """
        Decode and validate a JWT token.

        :param token: JWT token string to decode.
        :return: Decoded token payload as a dictionary.
        :raises TokenExpiredError: If the token has expired.
        :raises InvalidTokenError: If the token is invalid or malformed.
        :raises TokenError: For other unknown token validation errors.
        """
        try:
            return jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
            )
        except ExpiredSignatureError as ex:
            raise TokenExpiredError("Token expired.") from ex
        except PyJWTInvalidTokenError as ex:
            raise InvalidTokenError("Invalid token.") from ex
        except Exception as ex:
            raise TokenError("Unknown token validation error.") from ex
