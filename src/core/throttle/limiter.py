"""
Request limiting module to prevent abuse by restricting the number of requests
"""

import time

from functools import wraps

from fastapi import Request

from src.core.settings import settings
from src.core.observability.logging import logger
from src.db.redis.broker import redis_client
from src.exceptions.api.common import BadRequestHTTPException
from src.exceptions.api.common import TooManyRequestsHTTPException


class RequestLimiter:
    """
    RequestLimiter class.
    :raises Exception: If class initialization or usage fails.
    """
    def __init__(self):
        """
          init  .

        :return: None.
        :raises Exception: If the operation fails.
        """
        self.limit_get = settings.rate_limit.limit_get
        self.limit_ppd = settings.rate_limit.limit_ppd
        self.time_get = settings.rate_limit.time_get
        self.time_ppd = settings.rate_limit.time_ppd
        self.enabled = settings.rate_limit.rate_limit_enabled

    def limiter(self, max_requests: int, period: int):
        """
        Limiter.

        :param max_requests: TODO - describe max_requests.
        :type max_requests: int
        :param period: TODO - describe period.
        :type period: int
        :return: TODO - describe return value.
        :raises BadRequestHTTPException: If the operation cannot be completed.
        :raises TooManyRequestsHTTPException: If the operation cannot be completed.
        """
        def decorator(func):
            """
            Decorator.

            :param func: TODO - describe func.
            :return: TODO - describe return value.
            :raises BadRequestHTTPException: If the operation cannot be completed.
            :raises TooManyRequestsHTTPException: If the operation cannot be completed.
            """
            @wraps(func)
            async def wrapper(*args, **kwargs):
                """
                Wrapper.

                :param args: TODO - describe args.
                :param kwargs: TODO - describe kwargs.
                :return: TODO - describe return value.
                :raises BadRequestHTTPException: If the operation cannot be completed.
                :raises TooManyRequestsHTTPException: If the operation cannot be completed.
                """
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
                    logger.warning(f"Rate limiter bypassed due to Redis error: {ex}")

                return await func(*args, **kwargs)

            return wrapper
        return decorator

    def get_limiter(self):
        """
        Get limiter.

        :return: TODO - describe return value.
        :raises Exception: If the operation fails.
        """
        return self.limiter(self.limit_get, self.time_get)

    def ppd_limiter(self):
        """
        Ppd limiter.

        :return: TODO - describe return value.
        :raises Exception: If the operation fails.
        """
        return self.limiter(self.limit_ppd, self.time_ppd)


limiter = RequestLimiter()
