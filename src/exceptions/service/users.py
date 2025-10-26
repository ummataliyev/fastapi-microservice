from src.exceptions.service.base import BaseServiceException
from src.exceptions.repository.users import UserNotFoundRepoException
from src.exceptions.repository.users import UserAlreadyExistsRepoException


class UsersServiceException(BaseServiceException):
    message = "User service operation failed"


class UserNotFound(UsersServiceException):
    message = "User not found"

    @classmethod
    def from_repo(cls, ex: UserNotFoundRepoException):
        """
        Convert repo-level exception to service-level.
        """
        return cls(f"{cls.message}: {ex}")


class UserAlreadyExists(UsersServiceException):
    message = "User already exists"

    @classmethod
    def from_repo(cls, ex: UserAlreadyExistsRepoException):
        """
        Convert repo-level exception to service-level.
        """
        return cls(f"{cls.message}: {ex}")
