"""
User model for authentication and user management.
"""

from sqlalchemy import text
from sqlalchemy import Index
from sqlalchemy import String
from sqlalchemy import CheckConstraint
from sqlalchemy import event

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from src.db.sqlalchemy import Base
from src.db.postgres.mixins import IDPkMixin
from src.db.postgres.mixins import TimestampMixin
from src.db.postgres.mixins import SoftDeletionMixin


class Users(Base, IDPkMixin, TimestampMixin, SoftDeletionMixin):
    """
    Database model representing a system user.

    Attributes:
        email (str): Unique email used for login.
        password (str): Hashed password of the user.
    """

    __table_args__ = (
        CheckConstraint(
            "email = lower(email)",
            name="ck_user_email_lowercase"
        ),
        Index("uq_user_email_lower", text("lower(email)"), unique=True),
    )

    email: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"


@event.listens_for(Users, "before_insert")
@event.listens_for(Users, "before_update")
def _normalize_email(mapper, connection, target):
    """Ensure email is always stored lowercase regardless of insert path."""
    if target.email:
        target.email = target.email.lower()
