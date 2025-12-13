"""
Redis Broker Module
"""

import redis

from src.core.config import settings


redis_client = redis.Redis(
    host=settings.redis.host,
    port=settings.redis.port,
    db=0,
    decode_responses=True
)
