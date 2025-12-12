"""
Async Transaction Manager

Concrete implementation of an async transaction manager
that initializes repositories and handles session commit/rollback.
"""

from typing import Type
from typing import TypeVar
from typing import Callable
from typing import Optional

from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession

from src.managers.base import BaseManager
from src.repositories.base import BaseRepository
from src.repositories.users import UsersRepository


T = TypeVar("T")


class TransactionManager(BaseManager):
    """
    Asynchronous transaction manager that handles database session lifecycle,
    commits, rollbacks, and repository initialization for easy access
    within an async context.
    """

    users: UsersRepository

    def __init__(
        self,
        session_factory: Callable[[], AsyncSession],
        **repositories: Type[BaseRepository],
    ):
        """
        Initialize the transaction manager.

        :param session_factory: Callable returning an AsyncSession.
        :param repositories: Optional extra repository classes to include.

        """
        self.session_factory = session_factory
        self._repositories = {
            "users": UsersRepository,
            **repositories
        }

    async def __aenter__(self) -> "TransactionManager":
        """
        Enter the asynchronous context manager.

        :return: The TransactionManager instance with initialized repositories.
        :rtype: TransactionManager
        """
        self.session = await self.session_factory().__aenter__()
        for name, repo_cls in self._repositories.items():
            setattr(self, name, repo_cls(self.session))
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """
        Exit the asynchronous context manager.

        :param exc_type: Exception type, if any.
        :param exc_val: Exception instance, if any.
        :param exc_tb: Traceback, if any.
        :return: None
        """
        if exc_type:
            await self.session.rollback()
        await self.session.close()

    async def commit(self) -> None:
        """
        Commit the current transaction.

        :return: None
        """
        await self.session.commit()

    async def rollback(self) -> None:
        """
        Rollback the current transaction.

        :return: None
        """
        await self.session.rollback()
