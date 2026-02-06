"""
Authentication related exceptions.
"""

from src.exceptions.service.base import BaseServiceException


class AuthException(BaseServiceException):
    """
    Base authentication exception.
    """

    message = "Authentication error"
    error_code = "AUTH_ERROR"


class InvalidCredentials(AuthException):
    """
    Raised when credentials are invalid.
    """

    message = "Invalid email or password"
    error_code = "AUTH_INVALID_CREDENTIALS"


class InvalidToken(AuthException):
    """
    Raised when token is invalid or expired.
    """

    message = "Invalid or expired token"
    error_code = "AUTH_INVALID_TOKEN"


class TokenExpired(AuthException):
    """
    Raised when token has expired.
    """

    message = "Token has expired"
    error_code = "AUTH_TOKEN_EXPIRED"


class InvalidTokenType(AuthException):
    """
    Raised when token type doesn't match expected type.
    """

    def __init__(self, expected: str, got: str):
        """
          init  .

        :param expected: TODO - describe expected.
        :type expected: str
        :param got: TODO - describe got.
        :type got: str
        :return: None.
        :raises Exception: If the operation fails.
        """
        super().__init__(
            message=f"Expected {expected} token, got {got}",
            details={"expected": expected, "got": got},
        )
        self.error_code = "AUTH_INVALID_TOKEN_TYPE"


class LoginTemporarilyLocked(AuthException):
    """Raised when login is temporarily blocked due to repeated failures."""

    def __init__(self, retry_after_seconds: int):
        """
          init  .

        :param retry_after_seconds: TODO - describe retry_after_seconds.
        :type retry_after_seconds: int
        :return: None.
        :raises Exception: If the operation fails.
        """
        self.retry_after_seconds = retry_after_seconds
        super().__init__(
            message=f"Too many failed login attempts. Try again in {retry_after_seconds} seconds.", # noqa
            details={"retry_after_seconds": retry_after_seconds},
        )
        self.error_code = "AUTH_LOGIN_TEMP_LOCKED"
