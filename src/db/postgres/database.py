"""
Database Base models configuration for PostgreSQL.
"""

import re
import inflect

from sqlalchemy import NullPool
from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker


from src.config import settings

async_engine = create_async_engine(
    url=settings.postgres.url,
    echo=settings.postgres.echo,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
)

async_engine_null_pull = create_async_engine(
    url=settings.postgres.url,
    poolclass=NullPool,
    echo=settings.postgres.echo,
)

async_session = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
)

async_session_null_pool = async_sessionmaker(
    async_engine_null_pull,
    expire_on_commit=False,
)

inflect_engine = inflect.engine()


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models with automatic table naming.

    Converts CamelCase class names into plural snake_case table names.
    """

    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        name = re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()
        return inflect_engine.plural(name)
