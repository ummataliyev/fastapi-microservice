"""
HTTP exception definitions for users.
"""

from fastapi import status

from src.exceptions.api.base import BaseHTTPException
from src.exceptions.schema.base import BaseHTTPExceptionSchema


class UserHTTPException(BaseHTTPException):
    """
    UserHTTPException class.

    :raises Exception: If class initialization or usage fails.
    """

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "User operation failed"
    error_code = "USER_HTTP_ERROR"
    schema = BaseHTTPExceptionSchema


class UserNotFoundHTTPException(UserHTTPException):
    """
    UserNotFoundHTTPException class.

    :raises Exception: If class initialization or usage fails.
    """

    status_code = status.HTTP_404_NOT_FOUND
    message = "User not found"
    error_code = "USER_NOT_FOUND"


class UserAlreadyExistsHTTPException(UserHTTPException):
    """
    UserAlreadyExistsHTTPException class.

    :raises Exception: If class initialization or usage fails.
    """

    status_code = status.HTTP_409_CONFLICT
    message = "User already exists"
    error_code = "USER_ALREADY_EXISTS"


class InvalidUsersInputHTTPException(UserHTTPException):
    """
    InvalidUsersInputHTTPException class.

    :raises Exception: If class initialization or usage fails.
    """

    status_code = status.HTTP_400_BAD_REQUEST
    message = "Invalid users request parameters"
    error_code = "USER_INVALID_INPUT"
