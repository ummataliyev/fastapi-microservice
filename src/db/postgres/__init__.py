"""
Register models for PostgreSQL.
"""

from src.db.postgres.database import Base
from src.models.users import Users


__all__ = [
    "Base",
    "Users",
]
