"""
Pagination schemas for API requests and responses.
"""

from typing import List
from typing import TypeVar
from typing import Generic
from typing import Annotated

from fastapi import Query

from pydantic import BaseModel

from src.core.config import settings


T = TypeVar("T")


class PaginationRequestSchema(BaseModel):
    """
    Schema for paginated requests from the client.

    :param page: Current page number (>=1, default=1).
    :param per_page: Number of items per page (default=10, max from settings).
    :return: Pagination request schema.
    """

    page: Annotated[
        int,
        Query(default=1, ge=1, description="Current page number (>=1)"),
    ]
    per_page: Annotated[
        int,
        Query(
            default=10,
            ge=1,
            le=settings.pagination.max_entities_per_page,
            description="Items per page",
        ),
    ]


class PaginationSchema(BaseModel):
    """
    Schema for internal pagination calculations.

    Transforms `page` & `per_page` into DB query params.

    :param limit: Maximum number of items to retrieve.
    :param offset: Number of items to skip before collecting results.
    :param current_page: Current page number (>=1).
    :return: Internal pagination schema.
    """

    limit: int
    offset: int
    current_page: int


class PaginationMetaScheme(BaseModel):
    """
    Metadata about pagination for API responses.

    :param total_pages: Total number of pages available.
    :param current_page: Current page number returned.
    :param total_items: Total number of items in the dataset.
    :param has_next_page: Whether there is a next page.
    :param has_previous_page: Whether there is a previous page.
    :return: Pagination metadata schema.
    """

    total_pages: int
    current_page: int
    total_items: int
    has_next_page: bool
    has_previous_page: bool


class PaginatedResponseSchema(BaseModel, Generic[T]):
    """
    Generic paginated response schema.

    :param status: Response status (e.g., "success").
    :param message Human-readable detail message.
    :param pagination: Metadata about pagination.
    :param data: List of serialized items for the current page.
    :return: Paginated API response schema.
    """

    status: str
    message: str
    pagination: PaginationMetaScheme
    data: List[T]
