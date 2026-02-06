"""
Repository exception definitions for users.
"""

from src.exceptions.repository.base import BaseRepoException


class UsersRepoException(BaseRepoException):
    """
    UsersRepoException class.

    :raises Exception: If class initialization or usage fails.
    """

    message = "Users repository error"
    error_code = "USERS_REPOSITORY_ERROR"


class UserNotFoundRepoException(UsersRepoException):
    """
    UserNotFoundRepoException class.

    :raises Exception: If class initialization or usage fails.
    """

    message = "User not found"
    error_code = "USERS_REPOSITORY_NOT_FOUND"


class UserAlreadyExistsRepoException(UsersRepoException):
    """
    UserAlreadyExistsRepoException class.

    :raises Exception: If class initialization or usage fails.
    """

    message = "User already exists"
    error_code = "USERS_REPOSITORY_ALREADY_EXISTS"
