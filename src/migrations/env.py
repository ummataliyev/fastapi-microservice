"""
Migration environment setup for Alembic + async SQLAlchemy.
"""

import asyncio

from alembic import context

from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from src.core.settings import settings
from src.db.sqlalchemy import Base
from src.models.users import Users  # noqa: F401


config = context.config


def _resolve_sqlalchemy_url() -> str:
    """
     resolve sqlalchemy url.

    :return: TODO - describe return value.
    :rtype: str
    :raises RuntimeError: If the operation cannot be completed.
    """
    provider = settings.db_provider.lower()
    if provider == "postgres":
        return settings.postgres.build_url()
    if provider == "mysql":
        return settings.mysql.url
    if provider == "mongo":
        raise RuntimeError(
            "Alembic migrations are not supported for DB_PROVIDER=mongo. "
            "Use a Mongo migration strategy (e.g., mongock/custom scripts)."
        )
    raise RuntimeError(f"Unsupported DB provider for migrations: {provider}")


config.set_main_option("sqlalchemy.url", _resolve_sqlalchemy_url())

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode (generates SQL scripts without DB connection).
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """
    Execute migrations using a given connection.
    """
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode using async engine.
    """
    connectable = create_async_engine(
        _resolve_sqlalchemy_url(),
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
