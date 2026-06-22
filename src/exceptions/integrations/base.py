from http import HTTPStatus

from src.exceptions.services.base import BaseServiceException


class IntegrationError(BaseServiceException):
    """Root for failures talking to an upstream/external service.

    Subclasses BaseServiceException so the registered exception handler maps
    it to an HTTP response automatically (see api/handlers/exceptions.py).
    """

    status_code = HTTPStatus.BAD_GATEWAY  # 502


class UpstreamUnavailableError(IntegrationError):
    """Upstream was unreachable, timed out, or returned 5xx after retries."""

    status_code = HTTPStatus.SERVICE_UNAVAILABLE  # 503


class UpstreamResponseError(IntegrationError):
    """Upstream returned a 4xx — our request was rejected (not retried).

    `upstream_status` carries the original status code so callers can react
    to specific cases (e.g. treat 404 as "not found" and return None).
    """

    status_code = HTTPStatus.BAD_GATEWAY  # 502

    def __init__(
        self,
        message: str = "Upstream rejected the request",
        *,
        upstream_status: int | None = None,
    ) -> None:
        super().__init__(message)
        self.upstream_status = upstream_status
