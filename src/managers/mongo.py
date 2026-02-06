"""
Mongo async managers.
"""

from typing import Type
from typing import Optional
from types import TracebackType

from src.managers.base import BaseAsyncManager
from src.managers.base import BaseTransactionManager
from src.repositories.mongo_users import MongoUsersRepository


class MongoReadonlyManager(BaseAsyncManager):
    """
    Read-only manager for Mongo provider.
    """

    users: MongoUsersRepository

    def __init__(self, database, **repositories: Type[MongoUsersRepository]):
        """
          init  .

        :param database: TODO - describe database.
        :param repositories: TODO - describe repositories.
        :type repositories: Type[MongoUsersRepository]
        :return: None.
        :raises Exception: If the operation fails.
        """
        self.database = database
        self._repositories = {
            "users": MongoUsersRepository,
            **repositories,
        }

    async def __aenter__(self) -> "MongoReadonlyManager":
        """
          aenter  .

        :return: TODO - describe return value.
        :rtype: 'MongoReadonlyManager'
        :raises Exception: If the operation fails.
        """
        self.session = self.database
        for name, repo_cls in self._repositories.items():
            setattr(self, name, repo_cls(self.database))
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """
          aexit  .

        :param exc_type: TODO - describe exc_type.
        :type exc_type: Optional[type[BaseException]]
        :param exc_val: TODO - describe exc_val.
        :type exc_val: Optional[BaseException]
        :param exc_tb: TODO - describe exc_tb.
        :type exc_tb: Optional[TracebackType]
        :return: None.
        :raises Exception: If the operation fails.
        """
        return None


class MongoTransactionManager(BaseTransactionManager):
    """
    Transaction manager for Mongo provider.

    Current implementation is operation-atomic and treats commit/rollback as no-ops.
    """

    users: MongoUsersRepository

    def __init__(self, database, **repositories: Type[MongoUsersRepository]):
        """
          init  .

        :param database: TODO - describe database.
        :param repositories: TODO - describe repositories.
        :type repositories: Type[MongoUsersRepository]
        :return: None.
        :raises Exception: If the operation fails.
        """
        self.database = database
        self._repositories = {
            "users": MongoUsersRepository,
            **repositories,
        }

    async def __aenter__(self) -> "MongoTransactionManager":
        """
          aenter  .

        :return: TODO - describe return value.
        :rtype: 'MongoTransactionManager'
        :raises Exception: If the operation fails.
        """
        self.session = self.database
        for name, repo_cls in self._repositories.items():
            setattr(self, name, repo_cls(self.database))
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """
          aexit  .

        :param exc_type: TODO - describe exc_type.
        :type exc_type: Optional[type[BaseException]]
        :param exc_val: TODO - describe exc_val.
        :type exc_val: Optional[BaseException]
        :param exc_tb: TODO - describe exc_tb.
        :type exc_tb: Optional[TracebackType]
        :return: None.
        :raises Exception: If the operation fails.
        """
        return None

    async def commit(self) -> None:
        """
        Commit.

        :return: None.
        :raises Exception: If the operation fails.
        """
        return None

    async def rollback(self) -> None:
        """
        Rollback.

        :return: None.
        :raises Exception: If the operation fails.
        """
        return None
