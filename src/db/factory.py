"""
Database provider factory.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.settings import settings
from src.managers.base import BaseAsyncManager
from src.managers.base import BaseTransactionManager
from src.managers.readonly import ReadonlyManager
from src.managers.transaction import TransactionManager


@dataclass(frozen=True)
class DBProviderBundle:
    """
    Runtime bundle for a selected DB provider.
    """

    transaction_session_factory: Callable[[], AsyncSession] | None
    readonly_session_factory: Callable[[], AsyncSession] | None
    transaction_manager_cls: type[BaseTransactionManager] | None
    readonly_manager_cls: type[BaseAsyncManager] | None
    transaction_manager_kwargs: dict[str, Any]
    readonly_manager_kwargs: dict[str, Any]
    repositories: dict[str, type[Any]]


def get_db_provider_bundle() -> DBProviderBundle:
    """
    Resolve provider-specific DB wiring from settings.

    Current state:
    - `postgres`: implemented with SQLAlchemy async sessions.
    - `mysql`, `mongo`: reserved for future adapters.
    """

    provider = settings.db_provider.lower()

    if provider == "postgres":
        from src.db.postgres.database import AsyncSessionLocal
        from src.db.postgres.database import AsyncSessionReadonly
        from src.repositories.users import UsersRepository

        return DBProviderBundle(
            transaction_session_factory=AsyncSessionLocal,
            readonly_session_factory=AsyncSessionReadonly,
            transaction_manager_cls=TransactionManager,
            readonly_manager_cls=ReadonlyManager,
            transaction_manager_kwargs={},
            readonly_manager_kwargs={},
            repositories={"users": UsersRepository},
        )

    if provider == "mysql":
        from src.db.mysql.database import AsyncSessionLocal
        from src.db.mysql.database import AsyncSessionReadonly
        from src.repositories.users import UsersRepository

        return DBProviderBundle(
            transaction_session_factory=AsyncSessionLocal,
            readonly_session_factory=AsyncSessionReadonly,
            transaction_manager_cls=TransactionManager,
            readonly_manager_cls=ReadonlyManager,
            transaction_manager_kwargs={},
            readonly_manager_kwargs={},
            repositories={"users": UsersRepository},
        )

    if provider == "mongo":
        from src.db.mongo.client import get_mongo_database
        from src.managers.mongo import MongoReadonlyManager
        from src.managers.mongo import MongoTransactionManager
        from src.repositories.mongo_users import MongoUsersRepository

        return DBProviderBundle(
            transaction_session_factory=None,
            readonly_session_factory=None,
            transaction_manager_cls=MongoTransactionManager,
            readonly_manager_cls=MongoReadonlyManager,
            transaction_manager_kwargs={"database": get_mongo_database()},
            readonly_manager_kwargs={"database": get_mongo_database()},
            repositories={"users": MongoUsersRepository},
        )

    raise ValueError(f"Unsupported DB provider: {provider}")


def build_transaction_manager() -> BaseTransactionManager:
    """
    Build transaction manager for active DB provider.
    """

    bundle = get_db_provider_bundle()
    if bundle.transaction_manager_cls is None:
        raise RuntimeError("Transaction manager class is not configured for provider")
    manager_cls = bundle.transaction_manager_cls
    manager_kwargs = {
        **bundle.transaction_manager_kwargs,
        **bundle.repositories,
    }
    if bundle.transaction_session_factory is not None:
        manager_kwargs["session_factory"] = bundle.transaction_session_factory
    return manager_cls(**manager_kwargs)


def build_readonly_manager() -> BaseAsyncManager:
    """
    Build readonly manager for active DB provider.
    """

    bundle = get_db_provider_bundle()
    if bundle.readonly_manager_cls is None:
        raise RuntimeError("Readonly manager class is not configured for provider")
    manager_cls = bundle.readonly_manager_cls
    manager_kwargs = {
        **bundle.readonly_manager_kwargs,
        **bundle.repositories,
    }
    if bundle.readonly_session_factory is not None:
        manager_kwargs["session_factory"] = bundle.readonly_session_factory
    return manager_cls(**manager_kwargs)
