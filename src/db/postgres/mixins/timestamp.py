"""
Timestamp mixins for database models.
"""

from datetime import datetime

from sqlalchemy import func
from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import declarative_mixin


@declarative_mixin
class TimestampMixin:
    """
    Adds automatic timestamp tracking for SQLAlchemy models.

    Attributes:
        created_at (datetime): The UTC timestamp when the record was created.
        updated_at (datetime): The UTC timestamp when the record was last updated.
            Automatically updated on record modification.
    """

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
