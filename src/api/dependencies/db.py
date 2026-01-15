from typing import Annotated

from fastapi import Depends

from src.db.postgres.database import AsyncSessionLocal
from src.db.postgres.database import AsyncSessionReadonly

from src.managers.readonly import ReadonlyManager
from src.managers.transaction import TransactionManager


async def get_db_transaction():
    """
    Provides a transactional database session as a FastAPI dependency.
    """
    async with TransactionManager(
        session_factory=AsyncSessionLocal,
    ) as transaction:
        yield transaction


async def get_db_readonly():
    """
    Provides a readonly database session as a FastAPI dependency.
    """
    async with ReadonlyManager(
        session_factory=AsyncSessionReadonly,
    ) as readonly:
        yield readonly


DbTransactionDep = Annotated[
    TransactionManager,
    Depends(get_db_transaction),
]

DbReadonlyDep = Annotated[
    ReadonlyManager,
    Depends(get_db_readonly)
]
