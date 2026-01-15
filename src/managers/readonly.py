"""
Async Readonly Manager

Concrete implementation of an async readonly manager
that exposes repositories WITHOUT transaction / commit / rollback.
"""

from typing import Type
from typing import Optional
from types import TracebackType

from collections.abc import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from src.managers.base import BaseAsyncManager

from src.repositories.base import BaseRepository
from src.repositories.users import UsersRepository


class ReadonlyManager(BaseAsyncManager):
    """
    Read-only async manager.

    This manager provides access to repositories using an async database
    session, but explicitly does NOT support transactions. No commit or
    rollback operations are performed.
    """

    users: UsersRepository

    def __init__(
        self,
        session_factory: Callable[[], AsyncSession],
        **repositories: Type[BaseRepository],
    ):
        """
        Initialize the readonly manager with a session factory and repositories.

        :param session_factory:
            Callable that returns an async session context manager.
        :param repositories:
            Optional additional repository classes to expose.
            The key is used as the attribute name on the manager.
        """

        self.session_factory = session_factory
        self._repositories = {
            "users": UsersRepository,
            **repositories,
        }

    async def __aenter__(self) -> "ReadonlyManager":
        """
        Enter the async context and initialize repositories.

        Opens a database session and attaches repository instances
        to the manager.

        :return:
            The initialized ReadonlyManager instance.
        """

        self.session = await self.session_factory().__aenter__()
        for name, repo_cls in self._repositories.items():
            setattr(self, name, repo_cls(self.session))
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ):
        """
        Exit the async context.

        Closes the database session. No commit or rollback is performed,
        regardless of whether an exception occurred.

        :param exc_type:
            The type of exception raised in the context, if any.
        :param exc_val:
            The exception instance raised in the context, if any.
        :param exc_tb:
            The traceback of the exception raised in the context, if any.
        :return:
            None
        """

        await self.session.close()
