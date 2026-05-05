"""
Request limiting module to prevent abuse by restricting the number of requests.
Falls back to an in-memory counter when Redis is unavailable.
"""

import time

from collections import defaultdict
from functools import wraps

from fastapi import Request

from src.core.settings import settings
from src.core.observability.logging import logger
from src.db.redis.broker import redis_client
from src.exceptions.api.common import BadRequestHTTPException
from src.exceptions.api.common import TooManyRequestsHTTPException


class RequestLimiter:
    """
    Rate limiter using Redis as the primary backend with an
    in-memory fallback when Redis is unreachable.
    """

    def __init__(self):
        self.limit_get = settings.rate_limit.limit_get
        self.limit_ppd = settings.rate_limit.limit_ppd
        self.time_get = settings.rate_limit.time_get
        self.time_ppd = settings.rate_limit.time_ppd
        self.enabled = settings.rate_limit.rate_limit_enabled
        self._fallback_counts: dict[str, int] = defaultdict(int)
        self._fallback_windows: dict[str, int] = {}

    def _check_fallback(self, key: str, max_requests: int, period: int) -> int:
        """
        In-memory fallback counter. Resets when the time window changes.

        :param key: Unique key identifying the client + action + window.
        :param max_requests: Maximum allowed requests per window.
        :param period: Window duration in seconds.
        :return: Current request count for this window.
        """
        current_window = int(time.time() // period)
        stored_window = self._fallback_windows.get(key)
        if stored_window != current_window:
            self._fallback_counts[key] = 0
            self._fallback_windows[key] = current_window
        self._fallback_counts[key] += 1
        return self._fallback_counts[key]

    def limiter(self, max_requests: int, period: int):
        """
        Create a rate-limiting decorator for an endpoint.

        :param max_requests: Maximum number of requests allowed per window.
        :param period: Time window duration in seconds.
        :return: Decorator that enforces the rate limit.
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                if not self.enabled:
                    return await func(*args, **kwargs)

                request: Request = kwargs.get("request")
                if not request:
                    raise BadRequestHTTPException(
                        detail="Request object missing",
                        error_code="REQUEST_OBJECT_MISSING",
                    )

                client_ip = request.client.host if request.client else "unknown"
                action = func.__name__
                current_window = int(time.time() // period)
                redis_key = f"throttle:{client_ip}:{action}:{current_window}"

                try:
                    request_count = await redis_client.incr(redis_key)
                    if request_count == 1:
                        await redis_client.expire(redis_key, period)
                    if int(request_count) > max_requests:
                        raise TooManyRequestsHTTPException(
                            detail="Too many requests. Please try again later.",
                            error_code="RATE_LIMIT_EXCEEDED",
                        )
                except (BadRequestHTTPException, TooManyRequestsHTTPException):
                    raise
                except Exception as ex:
                    logger.warning(f"Redis unavailable, using in-memory rate limiter: {ex}")
                    count = self._check_fallback(redis_key, max_requests, period)
                    if count > max_requests:
                        raise TooManyRequestsHTTPException(
                            detail="Too many requests. Please try again later.",
                            error_code="RATE_LIMIT_EXCEEDED",
                        )

                return await func(*args, **kwargs)

            return wrapper
        return decorator

    def get_limiter(self):
        """Return a rate-limit decorator configured for GET endpoints."""
        return self.limiter(self.limit_get, self.time_get)

    def ppd_limiter(self):
        """Return a rate-limit decorator configured for POST/PUT/DELETE endpoints."""
        return self.limiter(self.limit_ppd, self.time_ppd)


limiter = RequestLimiter()
