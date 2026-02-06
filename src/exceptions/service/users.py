"""
Service exception definitions for users.
"""

from src.exceptions.service.base import BaseServiceException
from src.exceptions.repository.users import UserNotFoundRepoException
from src.exceptions.repository.users import UserAlreadyExistsRepoException
from src.exceptions.repository.base import InvalidRepositoryInputRepoException


class UsersServiceException(BaseServiceException):
    """
    UsersServiceException class.

    :raises Exception: If class initialization or usage fails.
    """

    message = "User service operation failed"
    error_code = "USERS_SERVICE_ERROR"


class UserNotFound(UsersServiceException):
    """
    UserNotFound class.

    :raises Exception: If class initialization or usage fails.
    """

    message = "User not found"
    error_code = "USERS_NOT_FOUND"

    @classmethod
    def from_repo(cls, ex: UserNotFoundRepoException):
        """
        Convert repo-level exception to service-level.
        """
        return cls(message=cls.message, details={"source_error": str(ex)})


class UserAlreadyExists(UsersServiceException):
    """
    UserAlreadyExists class.

    :raises Exception: If class initialization or usage fails.
    """

    message = "User already exists"
    error_code = "USERS_ALREADY_EXISTS"

    @classmethod
    def from_repo(cls, ex: UserAlreadyExistsRepoException):
        """
        Convert repo-level exception to service-level.
        """
        return cls(message=cls.message, details={"source_error": str(ex)})


class InvalidUsersInput(UsersServiceException):
    """
    InvalidUsersInput class.

    :raises Exception: If class initialization or usage fails.
    """

    message = "Invalid users request parameters"
    error_code = "USERS_INVALID_INPUT"

    @classmethod
    def from_repo(cls, ex: InvalidRepositoryInputRepoException):
        """
        From repo.

        :param ex: TODO - describe ex.
        :type ex: InvalidRepositoryInputRepoException
        :return: TODO - describe return value.
        :raises Exception: If the operation fails.
        """
        return cls(message=cls.message, details={"source_error": str(ex)})
