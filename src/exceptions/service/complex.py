"""
Service Exceptions for Complex API endpoints.
"""

from src.exceptions.service.base import BaseServiceException
from src.exceptions.repository.complex import ComplexNotFoundRepoException
from src.exceptions.repository.complex import ComplexAlreadyExistsRepoException


class ComplexServiceException(BaseServiceException):
    """
    Base class for service-level exceptions related to Complex.
    """
    message = "Complex service operation failed"


class ComplexNotFound(ComplexServiceException):
    """
    Raised when a residential complex is not found in the system.
    """
    message = "Residential complex not found"

    @classmethod
    def from_repo(cls, ex: ComplexNotFoundRepoException):
        """
        Convert repo-level exception to service-level.
        """
        return cls(f"{cls.message}: {ex}")


class ComplexAlreadyExists(ComplexServiceException):
    """
    Raised when a residential complex already exists.
    """
    message = "Residential complex already exists"

    @classmethod
    def from_repo(cls, ex: ComplexAlreadyExistsRepoException):
        """
        Convert repo-level exception to service-level.
        """
        return cls(f"{cls.message}: {ex}")
