"""
Base HTTP client integration using httpx.AsyncClient.
Provides asynchronous GET, POST, DELETE methods with retries, circuit breaker,
timeout handling, and JSON response parsing.
"""

import httpx

from typing import Any
from typing import Optional

from src.core.config import settings
from src.core.resilience.retry import AsyncHTTPRetry
from src.core.resilience.circuit_breaker import CircuitBreakerFactory


class BaseHTTPClient:
    """
    Base asynchronous HTTP client with retry + circuit breaker.

    :param base_url: Base URL for the HTTP service.
    :param service_name: Unique name for the downstream service (used for circuit breaker).
    :param timeout: Optional timeout in seconds for HTTP requests.
    """

    def __init__(
        self,
        base_url: str,
        service_name: str,
        timeout: Optional[float] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.breaker = CircuitBreakerFactory(service_name)
        self.retry = AsyncHTTPRetry(
            attempts=settings.http_client.retries,
            min_wait=1,
            max_wait=5,
        )

        timeout_val = timeout or settings.http_client.timeout
        connect_timeout = settings.http_client.connect_timeout

        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout_val, connect=connect_timeout),
            limits=httpx.Limits(
                max_connections=settings.http_client.pool_maxsize,
                max_keepalive_connections=settings.http_client.pool_connections,
            ),
        )

    def _build_url(self, path: str) -> str:
        """
        Build the full URL for a given endpoint path.

        :param path: Endpoint path (e.g., "/users").
        :return: Full URL string.
        """
        return f"{self.base_url}{path}"

    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        """
        Perform a low-level HTTP request.

        :param method: HTTP method (GET, POST, DELETE, etc.).
        :param path: Endpoint path.
        :param kwargs: Additional arguments to pass to httpx.AsyncClient.request.
        :return: httpx.Response object.
        :raises httpx.HTTPStatusError: If the HTTP response status indicates an error.
        """
        url = self._build_url(path)
        response = await self.client.request(method, url, **kwargs)
        response.raise_for_status()
        return response

    async def _call(self, method: str, path: str, **kwargs) -> httpx.Response:
        """
        Execute HTTP request via retry and circuit breaker layers.

        :param method: HTTP method (GET, POST, DELETE, etc.).
        :param path: Endpoint path.
        :param kwargs: Additional keyword arguments for the request.
        :return: httpx.Response object.
        """
        retryable_request = self.retry.decorator()(self._request)
        return await self.breaker.call(retryable_request, method, path, **kwargs)

    async def get(self, path: str, params: Optional[dict[str, Any]] = None) -> dict:
        """
        Perform a GET request and return JSON response.

        :param path: Endpoint path.
        :param params: Optional query parameters.
        :return: Parsed JSON response as a dictionary.
        """
        response = await self._call("GET", path, params=params)
        return response.json()

    async def post(self, path: str, json: Optional[dict[str, Any]] = None) -> dict:
        """
        Perform a POST request with optional JSON body.

        :param path: Endpoint path.
        :param json: Optional JSON payload.
        :return: Parsed JSON response as a dictionary.
        """
        response = await self._call("POST", path, json=json)
        return response.json()

    async def delete(self, path: str, params: Optional[dict[str, Any]] = None) -> None:
        """
        Perform a DELETE request.

        :param path: Endpoint path.
        :param params: Optional query parameters.
        :return: None
        """
        await self._call("DELETE", path, params=params)

    async def post_no_content(
        self,
        path: str,
        json: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Perform a POST request expecting no content (204) or optional 404.

        :param path: Endpoint path.
        :param json: Optional JSON payload.
        :return: None
        :raises httpx.HTTPStatusError: If response status is unexpected.
        """
        response = await self._call("POST", path, json=json)
        if response.status_code not in (204, 404):
            response.raise_for_status()

    async def close(self) -> None:
        """
        Close the underlying HTTP client session.

        :return: None
        """
        await self.client.aclose()
