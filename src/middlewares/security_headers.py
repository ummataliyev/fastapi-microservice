"""
Middleware that injects baseline security headers into every response.
"""

from typing import Callable

from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds security headers that are safe defaults for API services.
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
        response = await call_next(request)
        path = request.url.path

        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("X-XSS-Protection", "1; mode=block")
        response.headers.setdefault(
            "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
        )
        if path.startswith("/docs") or path.startswith("/redoc") or path == "/openapi.json":
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https:; "
                "font-src 'self' https://fonts.gstatic.com; "
                "connect-src 'self'; "
                "frame-ancestors 'none';"
            )
        else:
            response.headers.setdefault(
                "Content-Security-Policy", "default-src 'self'; frame-ancestors 'none';"
            )
        return response
