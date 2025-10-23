"""
Initialization of database mixins.
"""

from src.db.postgres.mixins.pk import IDPkMixin
from src.db.postgres.mixins.timestamp import TimestampMixin
from src.db.postgres.mixins.softdeletion import SoftDeletionMixin


__all__ = (
    "IDPkMixin",
    "TimestampMixin",
    "SoftDeletionMixin",
)
