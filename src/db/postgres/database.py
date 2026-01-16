"""
Async SQLAlchemy engine/session and Base for template layout
"""

import re
import inflect

from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from src.core.settings import settings

engine = create_async_engine(
    settings.postgres.url,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True,
)

engine_readonly = create_async_engine(
    settings.postgres.url,
    pool_size=5,
    max_overflow=0,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

AsyncSessionReadonly = async_sessionmaker(
    bind=engine_readonly,
    expire_on_commit=False,
)

inflect_engine = inflect.engine()


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models with automatic table naming.

    Converts CamelCase class names into plural snake_case table names.
    All models inheriting from this base will automatically have
    `__tablename__` set according to this convention.
    """

    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        """
        Generate table name for the model.

        Converts the class name from CamelCase to snake_case
        and pluralizes it using the `inflect` library.

        :return: str - Pluralized snake_case table name.
        """
        name = re.sub(
            r"(?<!^)(?=[A-Z])",
            "_",
            cls.__name__,
        ).lower()
        return inflect_engine.plural(name)
