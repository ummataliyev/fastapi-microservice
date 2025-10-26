"""
Enums for models.
"""

from enum import Enum


class Status(str, Enum):
    """
    Enumeration of possible statuses.

    Members:
        UNDER_CONSTRUCTION: Currently under construction.
        COMPLETED: Construction or process has been completed.
        ACTIVE: Currently active and available.
        DELETED: Soft-deleted and not active.
    """

    UNDER_CONSTRUCTION = "under_construction"
    COMPLETED = "completed"
    ACTIVE = "active"
    DELETED = "deleted"
