"""
Centralized error handling middleware with structured error responses.
"""

import traceback

from typing import Callable

from fastapi import status
from fastapi.responses import JSONResponse

from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.observability.logging import logger
from src.exceptions.api.base import BaseHTTPException


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to catch and handle all exceptions, providing structured JSON
    error responses with proper logging and request ID tracking.
    """

    def __init__(self, app, debug: bool = False):
        """
        Initialize the middleware.

        :param app: FastAPI or Starlette application instance.
        :param debug: Enable debug mode to include detailed error info.
        """
        super().__init__(app)
        self.debug = debug

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process an incoming request and handle exceptions.

        :param request: Incoming HTTP request.
        :param call_next: Callable to execute the next middleware or route handler.
        :return: HTTP response, either normal or error JSON.
        """
        try:
            return await call_next(request)
        except BaseHTTPException as exc:
            return await self._handle_api_exception(request, exc)
        except ValueError as exc:
            return await self._handle_validation_error(request, exc)
        except Exception as exc:
            return await self._handle_unexpected_error(request, exc)

    async def _handle_api_exception(
        self, request: Request, exc: BaseHTTPException
    ) -> JSONResponse:
        """
        Handle custom API exceptions.

        :param request: Incoming HTTP request.
        :param exc: Raised BaseHTTPException instance.
        :return: JSONResponse with structured error details.
        """
        request_id = getattr(request.state, "request_id", "unknown")

        logger.warning(
            f"API exception | type={exc.__class__.__name__} "
            f"message={exc.message} path={request.url.path} request_id={request_id}"
        )

        error_response = {
            "error": {
                "type": exc.error_code or exc.__class__.__name__,
                "message": exc.message,
                "request_id": request_id,
            }
        }

        if self.debug and exc.details:
            error_response["error"]["details"] = exc.details

        return JSONResponse(status_code=exc.status_code, content=error_response)

    async def _handle_validation_error(
        self, request: Request, exc: ValueError
    ) -> JSONResponse:
        """
        Handle validation errors (e.g., ValueError).

        :param request: Incoming HTTP request.
        :param exc: Raised validation exception.
        :return: JSONResponse with 422 status code.
        """
        request_id = getattr(request.state, "request_id", "unknown")

        logger.warning(
            f"Validation error | message={str(exc)} "
            f"path={request.url.path} request_id={request_id}"
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "type": "ValidationError",
                    "message": str(exc),
                    "request_id": request_id,
                }
            },
        )

    async def _handle_unexpected_error(
        self, request: Request, exc: Exception
    ) -> JSONResponse:
        """
        Handle unexpected/unhandled exceptions.

        :param request: Incoming HTTP request.
        :param exc: Raised exception instance.
        :return: JSONResponse with 500 status code and optional debug info.
        """
        request_id = getattr(request.state, "request_id", "unknown")

        logger.error(
            f"Unexpected error | type={exc.__class__.__name__} "
            f"message={str(exc)} path={request.url.path} "
            f"method={request.method} request_id={request_id}",
            exc_info=True,
        )

        error_response = {
            "error": {
                "type": "InternalServerError",
                "message": "An unexpected error occurred",
                "request_id": request_id,
            }
        }

        if self.debug:
            error_response["error"]["debug"] = {
                "exception": exc.__class__.__name__,
                "message": str(exc),
                "traceback": traceback.format_exc().split("\n"),
            }

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response,
        )
