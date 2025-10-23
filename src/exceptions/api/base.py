"""
Base API exceptions.
"""

from fastapi import status
from fastapi import HTTPException


class BaseHTTPException(HTTPException):
    """
    Base class for custom HTTP exceptions in the API.

    Provides default values and easy inheritance for
    specialized exception types.

    Attributes:
        status_code (int): Default HTTP status code (500)
        message (str): Default error message
    """

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    message: str = "Internal server error"

    def __init__(
            self,
            detail: str | None = None,
            status_code: int | None = None
    ):
        super().__init__(
            status_code=status_code or self.status_code,
            detail=detail or self.message,
        )
