import time
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.core.observability.logging import get_logger

logger = get_logger(__name__)


class TimingMiddleware(BaseHTTPMiddleware):
    """Add `X-Process-Time` header and log slow requests."""

    HEADER = "X-Process-Time"

    def __init__(
        self,
        app,
        slow_threshold_ms: float = 1000.0,
        log_slow_requests: bool = True,
    ) -> None:
        super().__init__(app)
        self.slow_threshold_ms = slow_threshold_ms
        self.log_slow_requests = log_slow_requests

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        response.headers[self.HEADER] = f"{elapsed_ms:.2f}ms"
        request.state.process_time_ms = elapsed_ms

        if self.log_slow_requests and elapsed_ms > self.slow_threshold_ms:
            request_id = getattr(request.state, "request_id", "unknown")
            logger.warning(
                "Slow request | method=%s path=%s duration_ms=%.2f request_id=%s",
                request.method,
                request.url.path,
                elapsed_ms,
                request_id,
            )
        return response
