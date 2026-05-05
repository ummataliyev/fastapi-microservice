from sqlalchemy import CheckConstraint, Index, String, event, text
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import BaseModel


class Users(BaseModel):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("email = lower(email)", name="ck_user_email_lowercase"),
        Index("uq_user_email_lower", text("lower(email)"), unique=True),
    )

    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)


@event.listens_for(Users, "before_insert")
@event.listens_for(Users, "before_update")
def _normalize_email(mapper, connection, target):
    if target.email:
        target.email = target.email.lower()
