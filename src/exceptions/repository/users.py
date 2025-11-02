from src.exceptions.repository.base import BaseRepoException


class UsersRepoException(BaseRepoException):
    message = "Users repository error"


class UserNotFoundRepoException(UsersRepoException):
    message = "User not found"


class UserAlreadyExistsRepoException(UsersRepoException):
    message = "User already exists"
