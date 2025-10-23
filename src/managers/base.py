"""
Base async transaction manager utilities.

Defines the abstract interface for async transaction managers.
"""

from abc import ABC
from abc import abstractmethod

from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession


T = TypeVar("T")


class BaseManager(ABC):
    """
    Abstract base class for async transaction managers.

    Enforces methods for entering and exiting an async context,
    as well as committing transactions.
    """

    session: AsyncSession

    @abstractmethod
    async def __aenter__(self):
        """
        Enter the async context manager.

        :return: The manager instance.
        :rtype: BaseManager
        """

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the async context manager.

        :param exc_type: Exception type if raised within the context.
        :param exc_val: Exception instance if raised.
        :param exc_tb: Exception traceback if raised.
        :return: None
        """

    @abstractmethod
    async def commit(self):
        """
        Commit the current session transaction.

        :return: None
        """
