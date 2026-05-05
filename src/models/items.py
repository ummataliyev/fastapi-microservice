from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import BaseModel


class Items(BaseModel):
    __tablename__ = "items"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
