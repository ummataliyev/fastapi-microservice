"""
Package exports for exceptions.api.
"""

from src.exceptions.api.base import BaseHTTPException
from src.exceptions.api.auth import AuthHTTPException
from src.exceptions.api.users import UserHTTPException
from src.exceptions.api.common import BadRequestHTTPException
from src.exceptions.api.auth import InvalidTokenHTTPException
from src.exceptions.api.users import UserNotFoundHTTPException
from src.exceptions.api.common import UnauthorizedHTTPException
from src.exceptions.api.auth import AuthUserNotFoundHTTPException
from src.exceptions.api.common import TooManyRequestsHTTPException
from src.exceptions.api.auth import InvalidCredentialsHTTPException
from src.exceptions.api.users import UserAlreadyExistsHTTPException
from src.exceptions.api.users import InvalidUsersInputHTTPException
from src.exceptions.api.auth import LoginTemporarilyLockedHTTPException


__all__ = [
    "UserHTTPException",
    "BaseHTTPException",
    "AuthHTTPException",
    "BadRequestHTTPException",
    "InvalidTokenHTTPException",
    "UnauthorizedHTTPException",
    "UserNotFoundHTTPException",
    "TooManyRequestsHTTPException",
    "AuthUserNotFoundHTTPException",
    "UserAlreadyExistsHTTPException",
    "InvalidUsersInputHTTPException",
    "InvalidCredentialsHTTPException",
    "LoginTemporarilyLockedHTTPException",
]
