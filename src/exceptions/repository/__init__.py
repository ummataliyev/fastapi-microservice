"""
Package exports for exceptions.repository.
"""

from src.exceptions.repository.base import BaseRepoException
from src.exceptions.repository.users import UsersRepoException
from src.exceptions.repository.users import UserNotFoundRepoException
from src.exceptions.repository.base import ObjectNotFoundRepoException
from src.exceptions.repository.base import CannotAddObjectRepoException
from src.exceptions.repository.base import CannotUpdateObjectRepoException
from src.exceptions.repository.base import CannotDeleteObjectRepoException
from src.exceptions.repository.base import DatabaseConnectionRepoException
from src.exceptions.repository.users import UserAlreadyExistsRepoException
from src.exceptions.repository.base import InvalidRepositoryInputRepoException


__all__ = [
    "BaseRepoException",
    "UsersRepoException",
    "UserNotFoundRepoException",
    "ObjectNotFoundRepoException",
    "CannotAddObjectRepoException",
    "UserAlreadyExistsRepoException",
    "CannotUpdateObjectRepoException",
    "CannotDeleteObjectRepoException",
    "DatabaseConnectionRepoException",
    "InvalidRepositoryInputRepoException",
]
