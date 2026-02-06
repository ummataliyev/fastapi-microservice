"""
Backward-compatible settings module.
"""

from src.core.jwt import JWTSettings
from src.core.settings import Settings
from src.core.settings import settings
from src.core.redis import RedisSettings
from src.core.mongo import MongoSettings
from src.core.mysql import MySQLSettings
from src.core.postgres import PostgresSettings
from src.core.rate_limit import RateLimitSettings
from src.core.pagination import PaginationSettings
from src.core.http_client import HTTPClientSettings


__all__ = (
    "PostgresSettings",
    "HTTPClientSettings",
    "JWTSettings",
    "MongoSettings",
    "MySQLSettings",
    "PaginationSettings",
    "RateLimitSettings",
    "RedisSettings",
    "Settings",
    "settings",
)
