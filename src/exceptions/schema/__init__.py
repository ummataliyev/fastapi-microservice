"""
Package exports for exceptions.schema.
"""

from src.exceptions.schema.base import ErrorBodySchema
from src.exceptions.schema.base import BaseHTTPExceptionSchema


__all__ = [
    "ErrorBodySchema",
    "BaseHTTPExceptionSchema",
]
