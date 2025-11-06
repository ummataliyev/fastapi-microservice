"""
Async PostgreSQL test database and FastAPI client fixtures.
"""

import pytest

from httpx import AsyncClient
from httpx import ASGITransport

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from src.main import app
from src.db.postgres import Base
from src.core.config import settings
from src.managers.transaction import TransactionManager
from src.api.dependencies.db import get_db_transaction


TEST_DB_NAME = f"{settings.postgres.name}_test"


@pytest.fixture
async def create_test_database():
    """
    Creates a temporary test database and provides an async engine and session factory for tests.

    :yield: Tuple of (AsyncEngine, async_sessionmaker) connected to the test database.
    """
    TEST_DB_NAME = f"{settings.postgres.name}_test"

    default_engine = create_async_engine(
        f"postgresql+asyncpg://{settings.postgres.user}:{settings.postgres.password}"
        f"@{settings.postgres.host}:{settings.postgres.port}/postgres",
        isolation_level="AUTOCOMMIT",
    )

    async with default_engine.begin() as conn:
        await conn.execute(text(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}"'))
        await conn.execute(text(f'CREATE DATABASE "{TEST_DB_NAME}"'))

    test_async_engine = create_async_engine(
        f"postgresql+asyncpg://{settings.postgres.user}:{settings.postgres.password}"
        f"@{settings.postgres.host}:{settings.postgres.port}/{TEST_DB_NAME}",
        echo=False,
    )
    test_async_session = async_sessionmaker(test_async_engine, expire_on_commit=False)

    try:
        yield test_async_engine, test_async_session
    finally:
        await test_async_engine.dispose()
        async with default_engine.begin() as conn:
            await conn.execute(text(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}"'))
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
async def clean_db(create_test_database):
    """
    Cleans the test database by dropping and recreating all tables and extensions.

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
async def override_get_db(create_test_database):
    """
    Overrides the FastAPI dependency for database sessions to use the test database.
    Rolls back all changes after each usage to ensure test isolation.

    :param create_test_database: Fixture that provides the test database session factory.
    :yield: None
    """
    _, session_factory = create_test_database

    async def _get_db():
        async with TransactionManager(session_factory=session_factory) as transaction:
            yield transaction
            await transaction.rollback()

    app.dependency_overrides[get_db_transaction] = _get_db
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
