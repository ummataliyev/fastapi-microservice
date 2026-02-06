"""
Middleware that records Prometheus request metrics.
"""

import time

from typing import Callable

from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.observability.metrics import HTTP_REQUESTS_TOTAL
from src.core.observability.metrics import HTTP_REQUEST_DURATION_SECONDS


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Records request count and latency per method/path.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Dispatch.

        :param request: TODO - describe request.
        :type request: Request
        :param call_next: TODO - describe call_next.
        :type call_next: Callable
        :return: TODO - describe return value.
        :rtype: Response
        :raises Exception: If the operation fails.
        """
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start

        path = request.url.path
        method = request.method
        status_code = str(response.status_code)

        HTTP_REQUESTS_TOTAL.labels(
            method=method, path=path, status_code=status_code
        ).inc()
        HTTP_REQUEST_DURATION_SECONDS.labels(method=method, path=path).observe(duration)
        return response
