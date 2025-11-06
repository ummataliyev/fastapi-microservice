"""
Base schemas for API responses and common fields.
"""

from datetime import datetime

from pydantic import BaseModel


class BaseHTTPExceptionSchema(BaseModel):
    """
    Standard schema for API error responses.

    :param message Human-readable error message describing the issue.
    """

    message: str


class UUIDSchema(BaseModel):
    """
    Schema representing an object with a UUID primary key.

    :param id: Unique identifier (UUID) of the object.
    """

    id: int


class TimestampSchema(BaseModel):
    """
    Schema including creation and update timestamps.

    :param created_at: The datetime when the object was created.
    :param updated_at: The datetime when the object was last updated.
    """

    created_at: datetime
    updated_at: datetime
