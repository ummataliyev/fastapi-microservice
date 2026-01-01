"""
Middleware configuration for the FastAPI application.
"""
from fastapi import FastAPI

from src.middlewares.timing import TimingMiddleware
from src.middlewares.request_id import RequestIDMiddleware
from src.middlewares.cors import CORSMiddlewareConfigurator
from src.middlewares.error_handler import ErrorHandlerMiddleware


class MiddlewareManager:
    """
    Centralized middleware manager.

    Ensures correct ordering:
    1. Request ID
    2. Timing
    3. CORS
    4. Error Handler
    """

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.cors = CORSMiddlewareConfigurator()

    def setup(self, app: FastAPI) -> None:
        """
        Register middleware in expected execution order.
        """

        app.add_middleware(RequestIDMiddleware)

        app.add_middleware(
            TimingMiddleware,
            log_slow_requests=True,
            slow_threshold_ms=1000.0,
        )

        self.cors.configure(app)

        app.add_middleware(
            ErrorHandlerMiddleware,
            debug=self.debug,
        )
