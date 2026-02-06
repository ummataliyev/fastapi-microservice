"""
Shared SQLAlchemy declarative base and naming convention.
"""

import re
import inflect

from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import DeclarativeBase


inflect_engine = inflect.engine()


class Base(DeclarativeBase):
    """
    Base class for SQLAlchemy models with automatic singular snake_case names.
    """

    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        """
          tablename  .

        :return: TODO - describe return value.
        :rtype: str
        :raises Exception: If the operation fails.
        """
        name = re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()
        singular_name = inflect_engine.singular_noun(name)
        return singular_name if isinstance(singular_name, str) else name
