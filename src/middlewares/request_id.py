"""
Middleware to track requests with unique IDs for logging and debugging.
"""

import uuid

from typing import Callable

from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware that attaches a unique request ID to each incoming request.

    The request ID is:
    - Taken from the `X-Request-ID` header if provided by the client
    - Generated automatically if not provided
    - Stored in `request.state.request_id` for use in handlers and logging
    - Added to response headers for client visibility
    """

    def __init__(self, app, header_name: str = "X-Request-ID"):
        """
        Initialize the middleware.

        :param app: FastAPI or Starlette application instance
        :param header_name: HTTP header used to read/store the request ID
        """
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the incoming request and attach a unique request ID.

        :param request: Incoming HTTP request
        :param call_next: Callable to execute the next middleware or route handler
        :return: Response with the request ID header added
        """
        request_id = request.headers.get(self.header_name) or str(uuid.uuid4())

        request.state.request_id = request_id

        response = await call_next(request)
        response.headers[self.header_name] = request_id

        return response
