"""
Async SQLAlchemy engine/session for PostgreSQL.
"""

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from src.core.settings import settings
from src.db.sqlalchemy import Base

engine = create_async_engine(
    settings.postgres.url,
    pool_size=settings.postgres.pool_size,
    max_overflow=settings.postgres.max_overflow,
    pool_timeout=settings.postgres.pool_timeout,
    pool_recycle=settings.postgres.pool_recycle,
    pool_pre_ping=settings.postgres.pool_pre_ping,
)

engine_readonly = create_async_engine(
    settings.postgres.url,
    pool_size=settings.postgres.readonly_pool_size,
    max_overflow=settings.postgres.readonly_max_overflow,
    pool_timeout=settings.postgres.readonly_pool_timeout,
    pool_recycle=settings.postgres.readonly_pool_recycle,
    pool_pre_ping=settings.postgres.readonly_pool_pre_ping,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

AsyncSessionReadonly = async_sessionmaker(
    bind=engine_readonly,
    expire_on_commit=False,
)
