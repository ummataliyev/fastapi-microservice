"""
Unit tests for test health api.
"""

import pytest

from httpx import AsyncClient
from httpx import ASGITransport

from src.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    """
    Test health endpoint.

    :return: None.
    :raises Exception: If the operation fails.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_live_endpoint():
    """
    Test live endpoint.

    :return: None.
    :raises Exception: If the operation fails.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}
