"""
Base HTTP client integration using httpx.AsyncClient.
Provides basic GET, POST, DELETE methods with retries, timeout, and JSON response handling.
"""

import json
import httpx

from typing import Any
from typing import Optional

from src.core.config import settings


class BaseHTTPClient:
    """
    Base asynchronous HTTP client using httpx.AsyncClient.

    Provides basic GET, POST, DELETE methods with retries, timeout, and JSON response handling. # noqa

    :param base_url: The base URL for all HTTP requests.
    :param timeout: Optional timeout in seconds for the requests.
    """

    def __init__(self, base_url: str, timeout: Optional[float] = None):
        self.base_url = base_url.rstrip("/")
        timeout_val = timeout or settings.http_client.timeout
        connect_timeout = settings.http_client.connect_timeout
        retries = settings.http_client.retries

        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout_val, connect=connect_timeout),
            transport=httpx.AsyncHTTPTransport(retries=retries),
            limits=httpx.Limits(
                max_connections=settings.http_client.pool_maxsize,
                max_keepalive_connections=settings.http_client.pool_connections, # noqa
            ),
        )

    def _build_url(self, path: str) -> str:
        """
        Build the full URL by combining the base URL and the path.

        :param path: The endpoint path.
        :return: Full URL string.
        """
        return f"{self.base_url}{path}"

    async def get(
            self,
            path: str,
            params: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """
        Perform an HTTP GET request.

        :param path: Endpoint path.
        :param params: Optional query parameters.
        :return: JSON response as a dictionary.
        :raises httpx.HTTPStatusError: If the response status is an error.
        :raises Exception: For other unexpected errors.
        """
        url = self._build_url(path)
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def post(
            self,
            path: str,
            json: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """
        Perform an HTTP POST request.

        :param path: Endpoint path.
        :param json: Optional JSON body.
        :return: JSON response as a dictionary.
        :raises httpx.HTTPStatusError: If the response status is an error.
        :raises Exception: For other unexpected errors.
        """
        url = self._build_url(path)
        response = await self.client.post(url, json=json)
        response.raise_for_status()
        return response.json()

    async def delete(
            self,
            path: str,
            params: Optional[dict[str, Any]] = None
    ) -> None:
        """
        Perform an HTTP DELETE request.

        :param path: Endpoint path.
        :param params: Optional query parameters.
        :return: None
        :raises httpx.HTTPStatusError: If the response status is an error.
        :raises Exception: For other unexpected errors.
        """
        url = self._build_url(path)
        response = await self.client.delete(url, params=params)
        response.raise_for_status()

    async def post_no_content(
            self,
            path: str,
            params: Optional[dict[str, Any]] = None
    ) -> None:
        """
        Perform an HTTP POST request expecting no content (204) or optional 404.

        :param path: Endpoint path.
        :param json: Optional JSON body.
        :return: None
        :raises httpx.HTTPStatusError: If the response status is unexpected.
        :raises Exception: For other unexpected errors.
        """
        url = self._build_url(path)
        response = await self.client.post(url, json=json)
        if response.status_code not in (204, 404):
            response.raise_for_status()

    async def close(self) -> None:
        """
        Close the underlying HTTP client session.

        :return: None
        """
        await self.client.aclose()
