from sqlalchemy.ext.asyncio import AsyncSession


class BaseTransactionManager:
    """Owns one AsyncSession + a registry of repositories built on it."""

    session: AsyncSession

    def __init__(self) -> None:
        self._session_cm = None

    async def _open_session(self) -> AsyncSession:
        from src.db.postgres.instance import AsyncSessionFactory

        self._session_cm = AsyncSessionFactory()
        self.session = await self._session_cm.__aenter__()
        return self.session

    async def _close_session(self, exc_type, exc_val, exc_tb) -> None:
        if self._session_cm is not None:
            await self._session_cm.__aexit__(exc_type, exc_val, exc_tb)
            self._session_cm = None
