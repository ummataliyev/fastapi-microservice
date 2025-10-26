from fastapi import status

from src.exceptions.api.base import BaseHTTPException
from src.exceptions.schema.base import BaseHTTPExceptionSchema


class UserHTTPException(BaseHTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "User operation failed"
    schema = BaseHTTPExceptionSchema


class UserNotFoundHTTPException(UserHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    message = "User not found"


class UserAlreadyExistsHTTPException(UserHTTPException):
    status_code = status.HTTP_409_CONFLICT
    message = "User already exists"
