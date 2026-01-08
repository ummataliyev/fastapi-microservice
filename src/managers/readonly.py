"""
Async Readonly Manager

Concrete implementation of an async readonly manager
that exposes repositories WITHOUT transaction / commit / rollback.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.users import UsersRepository


class ReadonlyManager:
    """
    Read-only manager that exposes repositories
    WITHOUT transaction / commit / rollback.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

        self.user = UsersRepository(session)
