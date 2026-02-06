"""
Base API exceptions.
"""

from fastapi import status
from fastapi import HTTPException

from pydantic import BaseModel

from src.exceptions.schema.base import BaseHTTPExceptionSchema


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
    error_code: str | None = None
    details: dict | None = None
    schema: type[BaseModel] = BaseHTTPExceptionSchema

    def __init__(
        self,
        detail: str | None = None,
        status_code: int | None = None,
        error_code: str | None = None,
        details: dict | None = None,
        headers: dict[str, str] | None = None,
    ):
        """
          init  .

        :param detail: TODO - describe detail.
        :type detail: str | None
        :param status_code: TODO - describe status_code.
        :type status_code: int | None
        :param error_code: TODO - describe error_code.
        :type error_code: str | None
        :param details: TODO - describe details.
        :type details: dict | None
        :param headers: TODO - describe headers.
        :type headers: dict[str, str] | None
        :return: None.
        :raises Exception: If the operation fails.
        """
        self.message = detail or self.message
        self.error_code = error_code or self.error_code
        self.details = details
        super().__init__(
            status_code=status_code or self.status_code,
            detail=self.message,
            headers=headers,
        )
