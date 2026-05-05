from src.db.postgres.mixins import SoftDeletionMixin, TimestampMixin, UUIDPkMixin
from src.db.sqlalchemy.base import Base


class BaseModel(UUIDPkMixin, TimestampMixin, SoftDeletionMixin, Base):
    """UUID PK + created/updated timestamps + soft-delete column."""

    __abstract__ = True
