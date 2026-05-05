from typing import Annotated

from fastapi import Depends

from src.db.factory import readonly_manager_factory, transaction_manager_factory
from src.managers.db.readonly import ReadonlyManager
from src.managers.db.transaction import TransactionManager

DbTransactionDep = Annotated[TransactionManager, Depends(transaction_manager_factory)]
DbReadonlyDep = Annotated[ReadonlyManager, Depends(readonly_manager_factory)]
