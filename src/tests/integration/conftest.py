"""Pytest fixtures for integration tests against a real Postgres database.

Tests in `src/tests/integration/` require a running Postgres reachable via the
`DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_DATABASE` env vars (the same
ones the app uses). Locally, start one with:

    docker run -d --name fm-test-pg -p 5433:5432 \\
      -e POSTGRES_DB=template_service_db \\
      -e POSTGRES_USER=postgres \\
      -e POSTGRES_PASSWORD=postgres \\
      postgres:16-alpine

then run:

    DB_HOST=localhost DB_PORT=5433 DB_USER=postgres DB_PASSWORD=postgres \\
    DB_DATABASE=template_service_db \\
    uv run pytest src/tests/integration/ -v
"""
from collections.abc import AsyncIterator, Iterator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

import src.models  # noqa: F401  (registers every model on Base.metadata)
from src.core.settings import settings
from src.db.postgres import instance as db_instance
from src.db.sqlalchemy.base import Base


def _make_async_url(url: str) -> str:
    if url.startswith("postgresql+asyncpg://"):
        return url
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


# Replace the production engine with one that uses NullPool. With NullPool,
# every operation gets a fresh asyncpg connection on the current event loop
# and disposes it when done — there is no pool to leak loop-bound connections
# between tests. We patch the module attributes BEFORE importing `app` so any
# lazy `from src.db.postgres.instance import ...` inside request handlers
# picks up the test engine.
_test_engine = create_async_engine(
    _make_async_url(settings.database_url),
    echo=False,
    future=True,
    poolclass=NullPool,
)
_test_session_factory = async_sessionmaker(
    bind=_test_engine,
    expire_on_commit=False,
)
db_instance.engine = _test_engine
db_instance.AsyncSessionFactory = _test_session_factory

from src.main import app  # noqa: E402  (must come after the engine swap)


@pytest_asyncio.fixture(scope="session", autouse=True, loop_scope="session")
async def _schema() -> AsyncIterator[None]:
    """Create the schema once per session and drop it on teardown."""
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await _test_engine.dispose()


@pytest_asyncio.fixture(autouse=True, loop_scope="session")
async def _clean_tables() -> None:
    """Wipe data between tests without dropping the schema."""
    async with _test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(text(f'TRUNCATE TABLE "{table.name}" CASCADE'))


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c
