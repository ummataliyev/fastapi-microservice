"""
Schemas for HTTP exceptions.
"""

from typing import Any

from pydantic import Field
from pydantic import BaseModel


class ErrorBodySchema(BaseModel):
    """
    Structured error body returned by middleware.
    """

    type: str = Field(..., description="Stable error type/code")
    message: str = Field(..., description="Human-readable error message")
    request_id: str = Field(..., description="Request identifier for tracing")
    details: dict[str, Any] | None = Field(
        default=None,
        description="Optional machine-readable details",
    )


class BaseHTTPExceptionSchema(BaseModel):
    """
    Standard top-level API error envelope.
    """

    error: ErrorBodySchema
