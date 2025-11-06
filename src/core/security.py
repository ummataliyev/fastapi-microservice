"""
JWT Authentication and Password Security utilities.
"""

from typing import Any
from typing import Dict

from jose import jwt
from jose import JWTError

from datetime import datetime
from datetime import timedelta

from passlib.context import CryptContext

from src.core.config import settings


class JWTAuth:
    """
    Utility class for password hashing and JWT token handling.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a hashed password.

        :param plain_password: The plain text password.
        :param hashed_password: The hashed password to verify against.
        :return: True if password matches, False otherwise.
        """
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        """
        Hash a plain password using bcrypt.

        :param password: The plain text password to hash.
        :return: The hashed password.
        """
        return cls.pwd_context.hash(password)

    @classmethod
    def create_access_token(cls, data: Dict[str, Any], expires_delta: timedelta | None = None) -> str:
        """
        Create a JWT access token.

        :param data: Dictionary containing claims to encode in the token.
        :param expires_delta: Optional expiration time delta.
        :return: Encoded JWT token string.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.jwt.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, settings.jwt.SECRET_KEY, algorithm=settings.jwt.ALGORITHM)

    @classmethod
    def create_refresh_token(cls, data: Dict[str, Any], expires_delta: timedelta | None = None) -> str:
        """
        Create a JWT refresh token.

        :param data: Dictionary containing claims to encode in the token.
        :param expires_delta: Optional expiration time delta.
        :return: Encoded JWT token string.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(days=settings.jwt.REFRESH_TOKEN_EXPIRE_DAYS))
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, settings.jwt.SECRET_KEY, algorithm=settings.jwt.ALGORITHM)

    @classmethod
    def decode_token(cls, token: str) -> Dict[str, Any]:
        """
        Decode and validate a JWT token.

        :param token: JWT token string to decode.
        :return: Decoded token payload.
        :raises JWTError: If token is invalid or expired.
        """
        try:
            payload = jwt.decode(token, settings.jwt.SECRET_KEY, algorithms=[settings.jwt.ALGORITHM])
            return payload
        except JWTError as ex:
            raise ex
