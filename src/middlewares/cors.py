"""
CORS middleware configuration for FastAPI application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


class CORSMiddlewareConfigurator:
    """
    Configures and attaches CORS middleware to a FastAPI application.

    Features:
    - Can allow all origins in development
    - Supports custom allowed origins in production
    - Sets common headers, methods, and max-age
    """

    def __init__(
        self,
        allow_all_in_dev: bool = True,
        allowed_origins: list[str] | None = None,
    ):
        """
        Initialize the CORS configurator.

        :param allow_all_in_dev: If True, all origins are allowed (useful for dev)
        :param allowed_origins: List of allowed origins (used if not allowing all)
        """
        self.allow_all_in_dev = allow_all_in_dev
        self.allowed_origins = allowed_origins or ["*"]

    def configure(self, app: FastAPI) -> None:
        """
        Attach configured CORS middleware to the FastAPI app.

        :param app: FastAPI application instance
        :return: None
        """
        origins = ["*"] if self.allow_all_in_dev else self.allowed_origins

        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
            expose_headers=["X-Request-ID", "X-Process-Time"],
            max_age=600,
        )
