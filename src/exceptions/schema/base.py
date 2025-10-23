"""
Schemas for HTTP exceptions.
"""

from pydantic import BaseModel, Field


class BaseHTTPExceptionSchema(BaseModel):
    """
    Base schema for representing HTTP exceptions in API responses.

    This schema ensures consistent error responses across the API.
    """

    detail: str = Field(..., description="Description of the error message")
