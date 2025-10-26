"""
Migration environment setup for Alembic + async SQLAlchemy.
"""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

# ✅ Import application settings
from src.config import settings  # Adjust path if needed
from src.db.postgres.database import Base

# Alembic Config object
config = context.config

# Override sqlalchemy.url with dynamic Pydantic settings
config.set_main_option("sqlalchemy.url", settings.postgres.build_url())

# Logging config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata from SQLAlchemy Base models
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
        settings.postgres.build_url(),
        poolclass=pool.NullPool,  # Optional: avoid connection pooling during migrations
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


# Entry point
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
