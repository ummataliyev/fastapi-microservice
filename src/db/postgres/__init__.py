"""
Register models for PostgreSQL.
"""

from src.db.postgres.database import Base

from src.models.users import User


__all__ = [
    "Base",
    "User",
]
