"""
Enums for endpoints.
"""

from enum import Enum


class SortBy(str, Enum):
    ALPHABETICAL = "alphabetical"
    NEWEST = "newest"
    OLDEST = "oldest"
