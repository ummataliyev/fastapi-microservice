"""
Primary key mixins for database models using integer ID.
"""

from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import declarative_mixin


@declarative_mixin
class IDPkMixin:
    """
    Adds an auto-incrementing integer primary key column to a SQLAlchemy model.

    Attributes:
        id (int): Auto-incrementing primary key.
    """

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
