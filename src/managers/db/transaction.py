from src.managers.db.base import BaseTransactionManager
from src.repositories.users import UsersRepository


class TransactionManager(BaseTransactionManager):
    """Read/write session. Commits on clean exit, rolls back on exception."""

    users: UsersRepository

    async def __aenter__(self) -> "TransactionManager":
        await self._open_session()
        self._wire_repositories()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            if exc_type is not None:
                await self.session.rollback()
            else:
                await self.session.commit()
        finally:
            await self._close_session(exc_type, exc_val, exc_tb)

    def _wire_repositories(self) -> None:
        self.users = UsersRepository(self.session)
