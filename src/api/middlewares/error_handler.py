import traceback
from typing import Callable

from fastapi import status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.core.observability.logging import get_logger
from src.exceptions.services.base import BaseServiceException

logger = get_logger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Catch uncaught exceptions and return a structured 500.

    `BaseServiceException` is intentionally NOT caught here — those are handled
    by `register_exception_handlers`. This middleware is the final safety net.
    """

    def __init__(self, app, debug: bool = False) -> None:
        super().__init__(app)
        self.debug = debug

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except BaseServiceException:
            raise
        except Exception as exc:
            request_id = getattr(request.state, "request_id", "unknown")
            logger.error(
                "Unhandled exception | type=%s message=%s path=%s method=%s request_id=%s",
                exc.__class__.__name__,
                str(exc),
                request.url.path,
                request.method,
                request_id,
                exc_info=True,
            )
            payload: dict = {
                "detail": "Internal server error",
                "type": "InternalServerError",
                "request_id": request_id,
            }
            if self.debug:
                payload["debug"] = {
                    "exception": exc.__class__.__name__,
                    "message": str(exc),
                    "traceback": traceback.format_exc().splitlines(),
                }
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=payload,
            )
