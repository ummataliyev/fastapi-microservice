"""
Base async transaction manager utilities.

Defines the abstract interface for async transaction managers.
"""

from abc import ABC
from abc import abstractmethod

from typing import TypeVar
from typing import Optional
from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession


T = TypeVar("T")


class BaseAsyncManager(ABC):
    """
    Abstract base class for async managers.

    Enforces async context management and session lifecycle handling.
    """

    session: AsyncSession

    @abstractmethod
    async def __aenter__(self):
        """
        Enter the async context manager.

        :return: The manager instance.
        """

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ):
        """
        Exit the async context manager.

        :param exc_type: Exception type if raised within the context.
        :param exc_val: Exception instance if raised.
        :param exc_tb: Exception traceback if raised.
        :return: None
        """


class BaseTransactionManager(BaseAsyncManager):
    """
    Abstract base class for async transaction managers.

    Extends BaseAsyncManager with transactional capabilities.
    """

    @abstractmethod
    async def commit(self):
        """
        Commit the current session transaction.

        :return: None
        """
