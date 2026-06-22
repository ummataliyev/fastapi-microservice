"""
Base for external HTTP integrations (service-to-service calls).

`BaseIntegration` gives every client a shared async httpx client with:
  - a configurable base_url / timeout / retry policy
  - automatic auth-header injection (override `_auth_headers`)
  - retries with exponential backoff on transport errors and 5xx
  - upstream failures mapped to IntegrationError subclasses

`TokenAuthIntegration` adds OAuth2 password-grant login with a cached bearer
token (refreshed shortly before expiry) — the common pattern for calling
another internal service that issues JWTs.

DO NOT use synchronous I/O inside async clients (no `requests`, no
`time.sleep`). For unavoidable sync libraries (e.g. ftplib), wrap with
`asyncio.to_thread(...)`.

Usage::

    class MyServiceClient(BaseIntegration):
        base_url = settings.my_service_url
        timeout = 10.0

        async def get_thing(self, thing_id: str) -> dict:
            return await self._get(f"/things/{thing_id}")
"""

import asyncio
from typing import Any

import httpx

from src.core.observability.logging import get_logger
from src.exceptions.integrations.base import (
    UpstreamResponseError,
    UpstreamUnavailableError,
)

logger = get_logger(__name__)


class BaseIntegration:
    base_url: str = ""
    timeout: float = 10.0
    max_retries: int = 2  # retries AFTER the first attempt
    backoff_base: float = 0.2  # seconds; doubled each retry

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float | None = None,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.base_url = (base_url or self.base_url).rstrip("/")
        self.timeout = timeout if timeout is not None else self.timeout
        self._transport = transport  # injectable for tests (httpx.MockTransport)
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                transport=self._transport,
            )
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _auth_headers(self) -> dict[str, str]:
        """Override to inject auth (e.g. a Bearer token). Default: none."""
        return {}

    async def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        """Send a request with retries, auth injection and error mapping.

        Returns the raw response on success (2xx/3xx). Raises
        `UpstreamResponseError` on 4xx and `UpstreamUnavailableError` on
        transport errors or 5xx that survive retries.
        """
        client = await self._get_client()
        headers = {**(await self._auth_headers()), **kwargs.pop("headers", {})}

        last_exc: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                response = await client.request(method, path, headers=headers, **kwargs)
            except httpx.TransportError as exc:
                last_exc = exc
                logger.warning(
                    "%s %s%s transport error (attempt %s/%s): %s",
                    method, self.base_url, path,
                    attempt + 1, self.max_retries + 1, exc,
                )
            else:
                if response.status_code < 400:
                    return response
                if response.status_code >= 500:
                    last_exc = UpstreamUnavailableError(
                        f"{method} {path} -> {response.status_code}"
                    )
                    logger.warning(
                        "%s %s%s upstream %s (attempt %s/%s)",
                        method, self.base_url, path, response.status_code,
                        attempt + 1, self.max_retries + 1,
                    )
                else:
                    # 4xx: our request was rejected — retrying won't help.
                    raise UpstreamResponseError(
                        f"{method} {path} -> {response.status_code}: "
                        f"{response.text[:500]}",
                        upstream_status=response.status_code,
                    )

            if attempt < self.max_retries:
                await asyncio.sleep(self.backoff_base * (2**attempt))

        if isinstance(last_exc, UpstreamUnavailableError):
            raise last_exc
        raise UpstreamUnavailableError(
            f"{method} {self.base_url}{path} failed after "
            f"{self.max_retries + 1} attempts"
        ) from last_exc

    async def _json(self, method: str, path: str, **kwargs: Any) -> Any:
        response = await self._request(method, path, **kwargs)
        if not response.content:
            return None
        return response.json()

    async def _get(self, path: str, **kwargs: Any) -> Any:
        return await self._json("GET", path, **kwargs)

    async def _post(self, path: str, **kwargs: Any) -> Any:
        return await self._json("POST", path, **kwargs)

    async def _put(self, path: str, **kwargs: Any) -> Any:
        return await self._json("PUT", path, **kwargs)

    async def _patch(self, path: str, **kwargs: Any) -> Any:
        return await self._json("PATCH", path, **kwargs)

    async def _delete(self, path: str, **kwargs: Any) -> Any:
        return await self._json("DELETE", path, **kwargs)


class TokenAuthIntegration(BaseIntegration):
    """BaseIntegration that authenticates via OAuth2 password grant and caches
    the bearer token, refreshing it shortly before expiry.

    Subclasses set `login_path`, `username` and `password` (typically from
    settings), or override `_login()` for non-standard auth flows.
    """

    login_path: str = "/login"
    username: str = ""
    password: str = ""
    token_ttl: float = 12 * 3600  # fallback lifetime if upstream omits expires_in
    token_refresh_skew: float = 60.0  # refresh this many seconds before expiry

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._token: str | None = None
        self._token_expiry: float = 0.0  # monotonic deadline (loop.time())
        self._auth_lock = asyncio.Lock()

    async def _login(self) -> tuple[str, float]:
        """Authenticate and return ``(access_token, ttl_seconds)``.

        Uses the raw client directly (not `_request`) to avoid recursing back
        into `_auth_headers`. Override for non-password-grant auth.
        """
        client = await self._get_client()
        response = await client.post(
            self.login_path,
            data={
                "grant_type": "password",
                "username": self.username,
                "password": self.password,
                "scope": "",
                "client_id": "string",
                "client_secret": "string",
            },
            headers={
                "accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        if response.status_code >= 400:
            raise UpstreamUnavailableError(
                f"Auth to {self.base_url}{self.login_path} failed: "
                f"{response.status_code}"
            )
        data = response.json()
        ttl = float(data.get("expires_in", self.token_ttl))
        return data["access_token"], ttl

    async def _auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {await self._token_value()}"}

    async def _token_value(self) -> str:
        now = asyncio.get_event_loop().time()
        if self._token is not None and now < self._token_expiry:
            return self._token

        # Single-flight: only one coroutine re-authenticates at a time.
        async with self._auth_lock:
            now = asyncio.get_event_loop().time()
            if self._token is not None and now < self._token_expiry:
                return self._token
            token, ttl = await self._login()
            self._token = token
            self._token_expiry = now + max(0.0, ttl - self.token_refresh_skew)
            logger.info(
                "%s: authenticated, token cached for ~%ss",
                type(self).__name__, int(ttl),
            )
            return token
