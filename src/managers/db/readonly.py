from src.managers.db.base import BaseTransactionManager


class ReadonlyManager(BaseTransactionManager):
    """Read-only session. Always rolls back on exit (never commits)."""

    async def __aenter__(self) -> "ReadonlyManager":
        await self._open_session()
        self._wire_repositories()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            await self.session.rollback()
        finally:
            await self._close_session(exc_type, exc_val, exc_tb)

    def _wire_repositories(self) -> None:
        # Add read-only repositories here.
        return None
