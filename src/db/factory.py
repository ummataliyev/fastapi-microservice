from collections.abc import AsyncIterator

from src.managers.db.readonly import ReadonlyManager
from src.managers.db.transaction import TransactionManager


async def transaction_manager_factory() -> AsyncIterator[TransactionManager]:
    async with TransactionManager() as tm:
        yield tm


async def readonly_manager_factory() -> AsyncIterator[ReadonlyManager]:
    async with ReadonlyManager() as rm:
        yield rm
