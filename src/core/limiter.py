"""
Request limiting module to prevent abuse by restricting the number of requests
"""

import time

from functools import wraps

from fastapi import Request
from fastapi import HTTPException

from src.core.config import settings
from src.db.redis.broker import redis_client


class RequestLimiter:
    def __init__(self):
        self.limit_get = settings.rate_limit.limit_get
        self.limit_ppd = settings.rate_limit.limit_ppd
        self.time_get = settings.rate_limit.time_get
        self.time_ppd = settings.rate_limit.time_ppd
        self.enabled = settings.rate_limit.rate_limit_enabled

    def limiter(self, max_requests: int, period: int):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                if not self.enabled:
                    return await func(*args, **kwargs)

                request: Request = kwargs.get("request")
                if not request:
                    raise HTTPException(400, "Request object missing")

                client_ip = request.client.host
                action = func.__name__
                current_window = int(time.time() // period)
                redis_key = f"throttle:{client_ip}:{action}:{current_window}"

                request_count = redis_client.get(redis_key)
                if request_count and int(request_count) >= max_requests:
                    raise HTTPException(
                        status_code=429,
                        detail="Too many requests. Please try again later."
                    )

                redis_client.incr(redis_key)
                redis_client.expire(redis_key, period)

                return await func(*args, **kwargs)

            return wrapper
        return decorator

    def get_limiter(self):
        return self.limiter(self.limit_get, self.time_get)

    def ppd_limiter(self):
        return self.limiter(self.limit_ppd, self.time_ppd)


limiter = RequestLimiter()
