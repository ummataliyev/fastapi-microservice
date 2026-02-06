"""
Middleware manager for the FastAPI application.
"""

from fastapi import FastAPI

from starlette.middleware.trustedhost import TrustedHostMiddleware

from src.middlewares.timing import TimingMiddleware
from src.middlewares.metrics import MetricsMiddleware
from src.middlewares.request_id import RequestIDMiddleware
from src.middlewares.cors import CORSMiddlewareConfigurator
from src.middlewares.error_handler import ErrorHandlerMiddleware
from src.middlewares.security_headers import SecurityHeadersMiddleware

from src.core.settings import settings


class MiddlewareManager:
    """
    Centralized middleware manager for security, observability and error handling.
    """

    def __init__(self, debug: bool = False):
        """
          init  .

        :param debug: TODO - describe debug.
        :type debug: bool
        :return: None.
        :raises Exception: If the operation fails.
        """
        self.debug = debug
        self.cors = CORSMiddlewareConfigurator()

    def setup(self, app: FastAPI) -> None:
        """
        Register middleware in expected execution order.
        """

        app.add_middleware(RequestIDMiddleware)
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.trusted_hosts
        )
        app.add_middleware(SecurityHeadersMiddleware)
        app.add_middleware(MetricsMiddleware)

        app.add_middleware(
            TimingMiddleware,
            log_slow_requests=True,
            slow_threshold_ms=settings.slow_request_threshold_ms,
        )

        self.cors.configure(app)

        app.add_middleware(
            ErrorHandlerMiddleware,
            debug=self.debug,
        )
