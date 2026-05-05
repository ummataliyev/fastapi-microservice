from datetime import datetime, timezone
from uuid import uuid4

import jwt as pyjwt

from src.core.settings import settings
from src.schemas.users import UserReadSchema
from src.services.auth import AuthService


def _make_user() -> UserReadSchema:
    now = datetime.now(timezone.utc)
    return UserReadSchema(
        id=uuid4(),
        created_at=now,
        updated_at=now,
        email="alice@example.com",
    )


def test_issue_tokens_returns_decodable_access_and_refresh():
    user = _make_user()
    service = AuthService(db=None)  # _issue_tokens does not touch self.db

    tokens = service._issue_tokens(user)

    access = pyjwt.decode(
        tokens.access_token,
        settings.jwt.secret_key,
        algorithms=[settings.jwt.algorithm],
    )
    refresh = pyjwt.decode(
        tokens.refresh_token,
        settings.jwt.secret_key,
        algorithms=[settings.jwt.algorithm],
    )

    assert access["sub"] == str(user.id)
    assert access["type"] == "access"
    assert refresh["sub"] == str(user.id)
    assert refresh["type"] == "refresh"
    assert tokens.token_type == "bearer"
