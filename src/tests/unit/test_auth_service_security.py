"""
Unit tests for test auth service security.
"""

import time
import pytest

from types import SimpleNamespace

from unittest.mock import Mock
from unittest.mock import AsyncMock

from src.services.auth import AuthService

from src.schemas.auth import LoginSchema
from src.schemas.users import UserInternalSchema

from src.exceptions.service.auth import InvalidToken
from src.exceptions.service.auth import LoginTemporarilyLocked


def _build_service_with_db():
    """
     build service with db.

    :return: TODO - describe return value.
    :raises Exception: If the operation fails.
    """
    db = AsyncMock()
    db.users = AsyncMock()
    service = AuthService(db)
    service.password_hasher = Mock()
    return service, db


@pytest.mark.asyncio
async def test_login_rejected_when_lock_key_is_active(monkeypatch):
    """
    Test login rejected when lock key is active.

    :param monkeypatch: TODO - describe monkeypatch.
    :return: None.
    :raises Exception: If the operation fails.
    """
    service, db = _build_service_with_db()
    redis_mock = AsyncMock()
    redis_mock.ttl = AsyncMock(side_effect=[120, -2])
    monkeypatch.setattr("src.services.auth.redis_client", redis_mock)

    with pytest.raises(LoginTemporarilyLocked):
        await service.login(
            LoginSchema(email="user@example.com", password="secret123"),
            client_ip="127.0.0.1",
        )

    db.users.get_one.assert_not_called()


@pytest.mark.asyncio
async def test_refresh_rejects_revoked_token(monkeypatch):
    """
    Test refresh rejects revoked token.

    :param monkeypatch: TODO - describe monkeypatch.
    :return: None.
    :raises Exception: If the operation fails.
    """
    service, db = _build_service_with_db()
    service.token_service = SimpleNamespace(
        decode=Mock(return_value={
            "type": "refresh",
            "sub": "1",
            "jti": "old-jti",
            "exp": int(time.time()) + 300}
        )
    )

    redis_mock = AsyncMock()
    redis_mock.get = AsyncMock(side_effect=["1", "1"])
    monkeypatch.setattr("src.services.auth.redis_client", redis_mock)

    with pytest.raises(InvalidToken):
        await service.refresh_access_token("revoked-token")

    db.users.get_one.assert_not_called()


@pytest.mark.asyncio
async def test_refresh_rotates_token_and_revokes_old_jti(monkeypatch):
    """
    Test refresh rotates token and revokes old jti.

    :param monkeypatch: TODO - describe monkeypatch.
    :return: None.
    :raises Exception: If the operation fails.
    """
    service, db = _build_service_with_db()
    service.token_service = SimpleNamespace(
        decode=Mock(return_value={
            "type": "refresh",
            "sub": "1",
            "jti": "old-jti",
            "exp": int(time.time()) + 600
        }),
        create_access_token=Mock(return_value="access-new"),
        create_refresh_token=Mock(return_value="refresh-new"),
    )
    user = UserInternalSchema(
        id=1,
        email="user@example.com",
        password="hash",
        created_at="2025-01-01T00:00:00Z",
        updated_at="2025-01-01T00:00:00Z",
    )
    db.users.get_one.return_value = user

    redis_mock = AsyncMock()
    redis_mock.get = AsyncMock(side_effect=[None, "1"])
    redis_mock.delete = AsyncMock()
    redis_mock.set = AsyncMock()
    monkeypatch.setattr("src.services.auth.redis_client", redis_mock)
    monkeypatch.setattr("src.services.auth.uuid4", lambda: SimpleNamespace(hex="new-jti")) # noqa

    tokens = await service.refresh_access_token("good-token")

    assert tokens.access_token == "access-new"
    assert tokens.refresh_token == "refresh-new"
    redis_mock.delete.assert_any_await("auth:refresh:active:old-jti")
    redis_mock.set.assert_any_await("auth:refresh:active:new-jti", "1", ex=604800) # noqa
