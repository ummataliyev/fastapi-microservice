"""
Initialization of API dependencies.
"""

from src.api.dependencies.auth import CurrentUserDep
from src.api.dependencies.db import DbTransactionDep
from src.api.dependencies.pagination import PaginationDep


__all__ = (
    "CurrentUserDep",
    "PaginationDep",
    "DbTransactionDep",
)
