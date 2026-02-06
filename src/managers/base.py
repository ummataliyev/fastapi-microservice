"""
Base async transaction manager utilities.
"""

from abc import ABC
from abc import abstractmethod

from typing import Self
from typing import Any
from typing import TypeVar
from typing import Optional
from types import TracebackType


T = TypeVar("T")


class BaseAsyncManager(ABC):
    """
    Abstract base class for async managers.

    Enforces async context management and session lifecycle handling.
    """

    session: Any

    @abstractmethod
    async def __aenter__(self) -> Self:
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
    ) -> None:
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
    async def commit(self) -> None:
        """
        Commit the current session transaction.

        :return: None
        """

    @abstractmethod
    async def rollback(self) -> None:
        """
        Rollback the current session transaction.

        :return: None
        """
