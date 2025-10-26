"""
User model for authentication and user management.
"""

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from sqlalchemy import String
from src.db.postgres import Base
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

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    password: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    def __repr__(self) -> str:
        return f"<User(email={self.email})>"
