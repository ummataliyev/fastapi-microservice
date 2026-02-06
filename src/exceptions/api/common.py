"""
HTTP exception definitions for common.
"""

from fastapi import status

from src.exceptions.api.base import BaseHTTPException
from src.exceptions.schema.base import BaseHTTPExceptionSchema


class BadRequestHTTPException(BaseHTTPException):
    """
    BadRequestHTTPException class.

    :raises Exception: If class initialization or usage fails.
    """

    status_code = status.HTTP_400_BAD_REQUEST
    message = "Bad request"
    error_code = "BAD_REQUEST"
    schema = BaseHTTPExceptionSchema


class UnauthorizedHTTPException(BaseHTTPException):
    """
    UnauthorizedHTTPException class.

    :raises Exception: If class initialization or usage fails.
    """

    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Unauthorized"
    error_code = "UNAUTHORIZED"
    schema = BaseHTTPExceptionSchema


class TooManyRequestsHTTPException(BaseHTTPException):
    """
    TooManyRequestsHTTPException class.

    :raises Exception: If class initialization or usage fails.
    """

    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    message = "Too many requests"
    error_code = "TOO_MANY_REQUESTS"
    schema = BaseHTTPExceptionSchema
