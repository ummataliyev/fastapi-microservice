"""
Database transaction dependency for FastAPI routes.
"""

from typing import Annotated

from fastapi import Depends

from src.db.postgres.database import async_session
from src.managers.transaction import TransactionManager


async def get_db_transaction():
    """
    Provides a transactional database session as a FastAPI dependency.

    This function is used in FastAPI routes as a dependency to automatically
    handle the lifecycle of a database session, ensuring proper commit/rollback.

    :return: An asynchronous generator yielding a TransactionManager instance.
    :rtype: TransactionManager
    :raises Exception: Rolls back the transaction if an unhandled exception occurs.
    """

    async with TransactionManager(
        session_factory=async_session,
    ) as transaction:
        yield transaction


DbTransactionDep = Annotated[
    TransactionManager,
    Depends(get_db_transaction),
]
