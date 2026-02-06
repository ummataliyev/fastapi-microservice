"""
Async SQLAlchemy engine/session for MySQL.
"""

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from src.core.settings import settings
from src.db.sqlalchemy import Base


engine = create_async_engine(
    settings.mysql.url,
    pool_size=settings.mysql.pool_size,
    max_overflow=settings.mysql.max_overflow,
    pool_timeout=settings.mysql.pool_timeout,
    pool_recycle=settings.mysql.pool_recycle,
    pool_pre_ping=settings.mysql.pool_pre_ping,
)

engine_readonly = create_async_engine(
    settings.mysql.url,
    pool_size=settings.mysql.readonly_pool_size,
    max_overflow=settings.mysql.readonly_max_overflow,
    pool_timeout=settings.mysql.readonly_pool_timeout,
    pool_recycle=settings.mysql.readonly_pool_recycle,
    pool_pre_ping=settings.mysql.readonly_pool_pre_ping,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

AsyncSessionReadonly = async_sessionmaker(
    bind=engine_readonly,
    expire_on_commit=False,
)
