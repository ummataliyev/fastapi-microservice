"""
Repository Exceptions for Complex API endpoints.
"""

from src.exceptions.repository.base import BaseRepoException


class ComplexRepoException(BaseRepoException):
    """
    Base class for repository-level exceptions related to Complex.
    """
    message = "Complex repository error"


class ComplexNotFoundRepoException(ComplexRepoException):
    """
    Raised when a Complex object is not found in the database.
    """
    message = "Residential complex not found"


class ComplexAlreadyExistsRepoException(ComplexRepoException):
    """
    Raised when trying to create a Complex that already exists.
    """
    message = "Residential complex already exists"
