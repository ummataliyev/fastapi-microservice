"""
Re-export every model here so Alembic autogenerate can see them.

Example:
    from src.models.items import Item

    __all__ = ["Item"]
"""

from src.models.items import Items  # noqa: F401  (registered for alembic)
from src.models.users import Users  # noqa: F401  (registered for alembic)
