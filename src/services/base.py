"""
Base Service methods.
"""

from math import ceil

from typing import List
from typing import Union
from typing import TypeVar

from src.managers.readonly import ReadonlyManager
from src.managers.transaction import TransactionManager

from src.schemas.pagination import PaginationMetaScheme
from src.schemas.pagination import PaginatedResponseSchema


T = TypeVar("T")


class BaseService:
    """
    Base class for all application services.

    Provides:
        - Access to the database transaction manager (`self.db`).
        - Common helper methods for building standardized responses.

    Services that inherit from this class gain convenient access to
    database repositories and shared response utilities.
    """

    def __init__(
            self,
            db: Union[TransactionManager, ReadonlyManager, None] = None,
    ) -> None:
        """
        Initialize the service with an optional database transaction manager.

        :param db: The database transaction manager instance.
        :type db: TransactionManager | None
        """
        self._db = db

    @property
    def db(self) -> Union[TransactionManager, ReadonlyManager]:
        """
        Get the active database transaction manager.

        :return: The active transaction manager instance.
        :rtype: TransactionManager
        :raises RuntimeError: If no database transaction manager was provided.
        """

        if self._db is None:
            raise RuntimeError(
                "Database connection is required for this operation, "
                "but was not configured."
            )
        return self._db

    @staticmethod
    def build_paginated_response(
        *,
        items: List[T],
        total_items: int,
        current_page: int,
        per_page: int,
        message: str = "Success",
    ) -> PaginatedResponseSchema[T]:
        """
        Build a standardized paginated API response.

        :param items: List of items for the current page.
        :type items: List[T]
        :param total_items: Total number of items available across all pages.
        :type total_items: int
        :param current_page: Current page number (>= 1).
        :type current_page: int
        :param per_page: Number of items per page.
        :type per_page: int
        :param message Human-readable detail message (default: "Success").
        :type message str
        :return: PaginatedResponseSchema containing pagination metadata and data.
        :rtype: PaginatedResponseSchema[T]
        """

        total_pages = ceil(total_items / per_page) if per_page > 0 else 0
        return PaginatedResponseSchema[T](
            status="success",
            message=message,
            pagination=PaginationMetaScheme(
                total_pages=total_pages,
                current_page=current_page,
                total_items=total_items,
                has_next_page=current_page < total_pages,
                has_previous_page=current_page > 1,
            ),
            data=items,
        )
