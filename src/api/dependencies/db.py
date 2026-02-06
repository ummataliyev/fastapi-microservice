"""
Module documentation.
"""

from typing import Annotated

from fastapi import Depends

from src.managers.base import BaseAsyncManager
from src.managers.base import BaseTransactionManager

from src.db.factory import build_readonly_manager
from src.db.factory import build_transaction_manager


async def get_db_transaction():
    """
    Provides a transactional database session as a FastAPI dependency.
    """
    manager = build_transaction_manager()
    async with manager as transaction:
        yield transaction


async def get_db_readonly():
    """
    Provides a readonly database session as a FastAPI dependency.
    """
    manager = build_readonly_manager()
    async with manager as readonly:
        yield readonly


DbTransactionDep = Annotated[
    BaseTransactionManager,
    Depends(get_db_transaction),
]

DbReadonlyDep = Annotated[
    BaseAsyncManager,
    Depends(get_db_readonly)
]
