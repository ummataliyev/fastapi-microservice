"""
CORS middleware configuration for FastAPI application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.settings import settings


class CORSMiddlewareConfigurator:
    """
    Configures and attaches CORS middleware to a FastAPI application.

    Features:
    - Can allow all origins in development
    - Supports custom allowed origins in production
    - Sets common headers, methods, and max-age
    """

    def __init__(self, allowed_origins: list[str] | None = None):
        """
        Initialize the CORS configurator.

        :param allow_all_in_dev: If True, all origins are allowed (useful for dev)
        :param allowed_origins: List of allowed origins (used if not allowing all)
        """
        self.allowed_origins = allowed_origins or settings.allowed_origins

    def configure(self, app: FastAPI) -> None:
        """
        Attach configured CORS middleware to the FastAPI app.

        :param app: FastAPI application instance
        :return: None
        """
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.allowed_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
            expose_headers=["X-Request-ID", "X-Process-Time"],
            max_age=600,
        )
