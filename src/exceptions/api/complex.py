"""
Exceptions for Complex API endpoints.
"""

from fastapi import status

from src.exceptions.api.base import BaseHTTPException
from src.exceptions.schema.base import BaseHTTPExceptionSchema


class ComplexHTTPException(BaseHTTPException):
    """Base HTTP exception for Complex-related endpoints."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "Complex operation failed"
    schema = BaseHTTPExceptionSchema


class ComplexNotFoundHTTPException(ComplexHTTPException):
    """HTTP 404 for not found complex."""
    status_code = status.HTTP_404_NOT_FOUND
    message = "Residential complex not found"


class ComplexAlreadyExistsHTTPException(ComplexHTTPException):
    """HTTP 409 for already existing complex."""
    status_code = status.HTTP_409_CONFLICT
    message = "Residential complex already exists"
