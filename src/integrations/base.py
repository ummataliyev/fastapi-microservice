"""
Base for external HTTP integrations.

DO NOT use synchronous I/O inside async clients (no `requests`, no `time.sleep`).
For unavoidable sync libraries (e.g. ftplib), wrap with `asyncio.to_thread(...)`.
"""

from typing import Any

import httpx


class BaseIntegration:
    base_url: str
    timeout: float = 30.0

    def __init__(self, base_url: str | None = None, timeout: float | None = None) -> None:
        self.base_url = base_url or self.base_url
        self.timeout = timeout if timeout is not None else self.timeout
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        client = await self._get_client()
        response = await client.request(method, path, **kwargs)
        response.raise_for_status()
        return response

    async def get(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self.request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self.request("POST", path, **kwargs)
