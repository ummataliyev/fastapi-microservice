"""
HTTP exception definitions for auth.
"""

from fastapi import status

from src.exceptions.api.base import BaseHTTPException
from src.exceptions.schema.base import BaseHTTPExceptionSchema


class AuthHTTPException(BaseHTTPException):
    """
    AuthHTTPException class.

    :raises Exception: If class initialization or usage fails.
    """

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "Authentication operation failed"
    error_code = "AUTH_HTTP_ERROR"
    schema = BaseHTTPExceptionSchema


class InvalidCredentialsHTTPException(AuthHTTPException):
    """
    InvalidCredentialsHTTPException class.

    :raises Exception: If class initialization or usage fails.
    """

    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Invalid email or password"
    error_code = "AUTH_INVALID_CREDENTIALS"


class InvalidTokenHTTPException(AuthHTTPException):
    """
    InvalidTokenHTTPException class.

    :raises Exception: If class initialization or usage fails.
    """

    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Invalid or expired token"
    error_code = "AUTH_INVALID_TOKEN"


class LoginTemporarilyLockedHTTPException(AuthHTTPException):
    """
    LoginTemporarilyLockedHTTPException class.

    :raises Exception: If class initialization or usage fails.
    """

    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    message = "Too many failed login attempts"
    error_code = "AUTH_LOGIN_TEMP_LOCKED"


class AuthUserNotFoundHTTPException(AuthHTTPException):
    """
    AuthUserNotFoundHTTPException class.

    :raises Exception: If class initialization or usage fails.
    """

    status_code = status.HTTP_404_NOT_FOUND
    message = "User not found"
    error_code = "AUTH_USER_NOT_FOUND"
