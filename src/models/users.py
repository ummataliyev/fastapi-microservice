"""
User model for authentication and user management.
"""

from sqlalchemy import text
from sqlalchemy import Index
from sqlalchemy import String
from sqlalchemy import CheckConstraint

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
        """
          repr  .

        :return: TODO - describe return value.
        :rtype: str
        :raises Exception: If the operation fails.
        """
        return f"<User(email={self.email})>"
