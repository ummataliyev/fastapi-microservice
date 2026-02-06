"""
Redis Broker Module
"""

from redis import asyncio as redis

from src.core.settings import settings


redis_client = redis.Redis(
    host=settings.redis.host,
    port=settings.redis.port,
    db=settings.redis.db,
    decode_responses=True,
    socket_connect_timeout=settings.redis.socket_connect_timeout,
    socket_timeout=settings.redis.socket_timeout,
    health_check_interval=settings.redis.health_check_interval,
    retry_on_timeout=settings.redis.retry_on_timeout,
)
