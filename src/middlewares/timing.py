"""
Middleware to measure and log request execution time.
"""

import time

from typing import Callable

from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.observability.logging import logger


class TimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that measures request processing time and provides metrics.

    The processing time is:
    - Added to response headers (X-Process-Time)
    - Stored in request.state for metrics collection
    - Logged if the request exceeds a configurable slow threshold
    """

    def __init__(
        self,
        app,
        header_name: str = "X-Process-Time",
        log_slow_requests: bool = True,
        slow_threshold_ms: float = 1000.0,
    ):
        """
        Initialize the middleware.

        :param app: FastAPI or Starlette application instance
        :param header_name: HTTP header used to report request duration
        :param log_slow_requests: Whether to log requests exceeding threshold
        :param slow_threshold_ms: Threshold in milliseconds for logging slow requests
        """
        super().__init__(app)
        self.header_name = header_name
        self.log_slow_requests = log_slow_requests
        self.slow_threshold_ms = slow_threshold_ms

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Measure the processing time of a request and optionally log slow requests.

        :param request: Incoming HTTP request
        :param call_next: Callable to execute the next middleware or route handler
        :return: HTTP response with processing time header added
        """
        start_time = time.perf_counter()

        response = await call_next(request)

        process_time = time.perf_counter() - start_time
        process_time_ms = process_time * 1000

        response.headers[self.header_name] = f"{process_time_ms:.2f}ms"

        request.state.process_time = process_time

        if self.log_slow_requests and process_time_ms > self.slow_threshold_ms:
            request_id = getattr(request.state, "request_id", "unknown")
            logger.warning(
                f"Slow request detected | "
                f"method={request.method} "
                f"path={request.url.path} "
                f"duration={process_time_ms:.2f}ms "
                f"request_id={request_id}"
            )

        return response
