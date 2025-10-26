"""
Migration environment setup.
"""

from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy import engine_from_config
from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

# ✅ Import application settings
from src.config import settings  # Adjust path if needed
from src.db.postgres.database import Base

# Alembic Config object
config = context.config

# ✅ Override sqlalchemy.url with our dynamic Pydantic settings
config.set_main_option("sqlalchemy.url", settings.postgres.build_url())

# Logging config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata from SQLAlchemy Base models
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
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


async def run_migrations_online():
    connectable = create_async_engine(settings.postgres.url)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
