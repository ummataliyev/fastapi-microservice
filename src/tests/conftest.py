"""
Async PostgreSQL test database and FastAPI client fixtures.
"""

import pytest

from httpx import AsyncClient
from httpx import ASGITransport

from sqlalchemy import text
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from src.main import app
from src.db.sqlalchemy import Base
from src.core.settings import settings
from src.schemas.users import UserReadSchema
from src.managers.transaction import TransactionManager
from src.api.dependencies.db import get_db_transaction
from src.api.dependencies.auth import get_current_user


TEST_DB_NAME = f"{settings.postgres.db}_test"
ACTIVE_PROVIDER = settings.db_provider.lower()


def pytest_collection_modifyitems(config, items):
    """
    Pytest collection modifyitems.

    :param config: TODO - describe config.
    :param items: TODO - describe items.
    :return: None.
    :raises Exception: If the operation fails.
    """
    provider = ACTIVE_PROVIDER
    supported_markers = {"postgres", "mysql", "mongo"}
    for item in items:
        item_markers = {marker.name for marker in item.iter_markers()}
        selected = item_markers.intersection(supported_markers)
        if selected and provider not in selected:
            item.add_marker(
                pytest.mark.skip(reason=f"Test provider marker {selected} does not match DB_PROVIDER={provider}") # noqa
            )


@pytest.fixture(scope="session")
async def create_test_database():
    """
    Creates a temporary test database and provides an async engine and session factory for tests.

    :yield: Tuple of (AsyncEngine, async_sessionmaker) connected to the test database.
    """
    if ACTIVE_PROVIDER != "postgres":
        pytest.skip("create_test_database fixture is currently implemented only for postgres provider")
    TEST_DB_NAME = f"{settings.postgres.db}_test"

    default_engine = create_async_engine(
        f"postgresql+asyncpg://{settings.postgres.user}:{settings.postgres.password}" # noqa
        f"@{settings.postgres.host}:{settings.postgres.port}/postgres",
        isolation_level="AUTOCOMMIT",
        poolclass=NullPool,
    )

    async with default_engine.begin() as conn:
        await conn.execute(text(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}"'))
        await conn.execute(text(f'CREATE DATABASE "{TEST_DB_NAME}"'))

    test_async_engine = create_async_engine(
        f"postgresql+asyncpg://{settings.postgres.user}:{settings.postgres.password}" # noqa
        f"@{settings.postgres.host}:{settings.postgres.port}/{TEST_DB_NAME}",
        echo=False,
        poolclass=NullPool,
    )
    test_async_session = async_sessionmaker(test_async_engine, expire_on_commit=False) # noqa

    try:
        yield test_async_engine, test_async_session
    finally:
        await test_async_engine.dispose()
        async with default_engine.begin() as conn:
            await conn.execute(
                text(
                    "SELECT pg_terminate_backend(pid) "
                    "FROM pg_stat_activity "
                    "WHERE datname = :db_name AND pid <> pg_backend_pid()"
                ),
                {"db_name": TEST_DB_NAME},
            )
            await conn.execute(text(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}"')) # noqa
        await default_engine.dispose()


@pytest.fixture(scope="session")
async def prepare_db(create_test_database):
    """
    Prepares the test database schema and extensions before running tests.

    :param create_test_database: Fixture that provides the test database engine.
    :yield: None
    """
    engine, _ = create_test_database
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS btree_gin"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture
async def clean_db(prepare_db, create_test_database):
    """
    Cleans the test database by dropping and recreating all tables and extensions.

    :param create_test_database: Fixture that provides the test database engine.
    :yield: None
    """
    engine, _ = create_test_database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture
async def override_get_db(create_test_database):
    """
    Overrides the FastAPI dependency for database sessions to use the test database.
    Rolls back all changes after each usage to ensure test isolation.

    :param create_test_database: Fixture that provides the test database session factory.
    :yield: None
    """
    _, session_factory = create_test_database

    async def _get_db():
        """
         get db.

        :return: None.
        :raises Exception: If the operation fails.
        """
        async with TransactionManager(session_factory=session_factory) as transaction: # noqa
            yield transaction
            await transaction.rollback()

    async def _get_current_user() -> UserReadSchema:
        """
         get current user.

        :return: TODO - describe return value.
        :rtype: UserReadSchema
        :raises Exception: If the operation fails.
        """
        return UserReadSchema(
            id=1,
            email="test@example.com",
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
        )

    app.dependency_overrides[get_db_transaction] = _get_db
    app.dependency_overrides[get_current_user] = _get_current_user
    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def ac():
    """
    Provides an HTTPX AsyncClient for testing FastAPI routes.

    :yield: AsyncClient instance connected to the FastAPI app.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client
