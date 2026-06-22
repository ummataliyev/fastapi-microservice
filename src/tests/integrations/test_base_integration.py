"""Unit tests for BaseIntegration / TokenAuthIntegration.

Uses httpx.MockTransport (built into httpx) so no real network and no extra
test dependency. Each client is constructed with a hand-rolled handler that
records calls and returns canned responses.
"""

import httpx
import pytest

from src.exceptions.integrations.base import (
    UpstreamResponseError,
    UpstreamUnavailableError,
)
from src.integrations.base import BaseIntegration, TokenAuthIntegration


def _client(handler, *, max_retries: int = 2) -> BaseIntegration:
    c = BaseIntegration(
        base_url="http://upstream",
        transport=httpx.MockTransport(handler),
    )
    c.max_retries = max_retries
    c.backoff_base = 0.0  # no real sleeping in tests
    return c


@pytest.mark.asyncio
async def test_get_returns_json_on_success():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/things/1"
        return httpx.Response(200, json={"id": 1, "name": "thing"})

    client = _client(handler)
    assert await client._get("/things/1") == {"id": 1, "name": "thing"}


@pytest.mark.asyncio
async def test_retries_5xx_then_succeeds():
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] < 3:
            return httpx.Response(503)
        return httpx.Response(200, json={"ok": True})

    client = _client(handler, max_retries=2)
    assert await client._get("/x") == {"ok": True}
    assert calls["n"] == 3  # 1 initial + 2 retries


@pytest.mark.asyncio
async def test_5xx_exhausts_retries_raises_unavailable():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500)

    client = _client(handler, max_retries=1)
    with pytest.raises(UpstreamUnavailableError):
        await client._get("/x")


@pytest.mark.asyncio
async def test_4xx_raises_response_error_without_retry():
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(404, text="nope")

    client = _client(handler, max_retries=3)
    with pytest.raises(UpstreamResponseError) as exc:
        await client._get("/missing")
    assert exc.value.upstream_status == 404
    assert calls["n"] == 1  # 4xx is not retried


@pytest.mark.asyncio
async def test_transport_error_retried_then_raises_unavailable():
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        raise httpx.ConnectError("boom", request=request)

    client = _client(handler, max_retries=2)
    with pytest.raises(UpstreamUnavailableError):
        await client._get("/x")
    assert calls["n"] == 3


@pytest.mark.asyncio
async def test_token_auth_caches_token_across_requests():
    counts = {"login": 0, "data": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/login":
            counts["login"] += 1
            return httpx.Response(200, json={"access_token": "tok", "expires_in": 3600})
        counts["data"] += 1
        assert request.headers["Authorization"] == "Bearer tok"
        return httpx.Response(200, json={"ok": True})

    client = TokenAuthIntegration(
        base_url="http://upstream",
        transport=httpx.MockTransport(handler),
    )
    client.login_path = "/login"
    client.backoff_base = 0.0

    await client._get("/a")
    await client._get("/b")

    assert counts["login"] == 1  # authenticated once, token reused
    assert counts["data"] == 2
