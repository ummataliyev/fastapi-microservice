"""
Soft Deletion Mixin for SQLAlchemy Models
"""

from datetime import datetime
from datetime import timezone

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import declarative_mixin


@declarative_mixin
class SoftDeletionMixin:
    """
    Adds soft deletion support to SQLAlchemy models with helper methods.

    Attributes:
        deleted_at (datetime | None): Timestamp when the record was soft deleted.
            None if the record is active.
    """

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None, index=True
    )

    def soft_delete(self) -> None:
        """
        Mark the record as soft deleted by setting `deleted_at` to current UTC time.

        :return: None
        """
        self.deleted_at = datetime.now(timezone.utc)

    def restore(self) -> None:
        """
        Restore a previously soft-deleted record by setting `deleted_at` to None.

        :return: None
        """
        self.deleted_at = None

    @property
    def is_deleted(self) -> bool:
        """
        Check if the record has been soft deleted.

        :return: True if `deleted_at` is not None, False otherwise.
        """
        return self.deleted_at is not None
