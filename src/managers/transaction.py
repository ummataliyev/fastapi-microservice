"""
Async Transaction Manager

Concrete implementation of an async transaction manager
that initializes repositories and handles session commit/rollback.
"""

from typing import Type
from typing import TypeVar
from typing import Generic
from typing import Callable
from typing import Optional

from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession

from src.managers.base import BaseManager
from src.repositories.base import BaseRepository
from src.repositories.users import UsersRepository


T = TypeVar("T")


class TransactionManager(Generic[T], BaseManager):
    """
    Generic transaction manager that initializes repositories
    and manages database sessions with commit/rollback.
    """

    users: UsersRepository

    def __init__(
        self,
        session_factory: Callable[[], AsyncSession],
        **repositories: Type[BaseRepository],
    ):
        """
        Initialize the transaction manager with a session factory
        and optional repositories.

        :param session_factory: Callable that returns an AsyncSession.
        :param repositories: Additional repository classes to include.
        """

        self.session_factory = session_factory
        self._repositories = {
            "users": UsersRepository,
            **repositories,
        }

    async def __aenter__(self):
        """
        Enter the async context and initialize repositories.

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
    ):
        """
        Exit the async context.

        Rolls back the session if an exception occurred and closes the session.

        :param exc_type: The type of exception raised in the context, if any.
        :param exc_val: The exception instance raised in the context, if any.
        :param exc_tb: The traceback of the exception raised, if any.
        :return: None
        """

        if exc_type:
            await self.session.rollback()
        await self.session.close()

    async def commit(self):
        """
        Commit the current session transaction.

        :return: None
        """

        await self.session.commit()

    async def rollback(self):
        """
        Rollback the current session transaction.

        :return: None
        """

        await self.session.rollback()
