"""
Unit tests for test users service.
"""

import pytest

from unittest.mock import Mock
from unittest.mock import AsyncMock

from src.services.users import UsersService

from src.schemas.users import UserCreateSchema
from src.schemas.users import UserUpdateSchema
from src.schemas.users import UserInternalSchema

from src.exceptions.service.users import UserNotFound
from src.exceptions.service.users import UserAlreadyExists
from src.exceptions.repository.users import UserNotFoundRepoException
from src.exceptions.repository.users import UserAlreadyExistsRepoException


@pytest.fixture
def service_with_db():
    """
    Service with db.

    :return: TODO - describe return value.
    :raises Exception: If the operation fails.
    """
    db = AsyncMock()
    db.users = AsyncMock()
    service = UsersService(db)
    service.password_hasher = Mock()
    service.password_hasher.hash.side_effect = lambda value: f"hashed::{value}"
    return service, db


@pytest.mark.asyncio
async def test_create_hashes_password_before_save(service_with_db):
    """
    Test create hashes password before save.

    :param service_with_db: TODO - describe service_with_db.
    :return: None.
    :raises Exception: If the operation fails.
    """
    service, db = service_with_db
    data = UserCreateSchema(email="new@example.com", password="securepass")
    created = UserInternalSchema(
        id=1,
        email=data.email,
        password="$2b$12$fake.hash.value",
        created_at="2025-01-01T00:00:00Z",
        updated_at="2025-01-01T00:00:00Z",
    )

    db.users.get_one_or_none.return_value = None
    db.users.add.return_value = created

    result = await service.create(data)

    assert result.email == data.email
    assert data.password == "hashed::securepass"
    db.users.add.assert_awaited_once()
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_raises_when_user_exists(service_with_db):
    """
    Test create raises when user exists.

    :param service_with_db: TODO - describe service_with_db.
    :return: None.
    :raises Exception: If the operation fails.
    """
    service, db = service_with_db
    data = UserCreateSchema(email="existing@example.com", password="securepass")
    db.users.get_one_or_none.return_value = UserInternalSchema(
        id=2,
        email=data.email,
        password="hash",
        created_at="2025-01-01T00:00:00Z",
        updated_at="2025-01-01T00:00:00Z",
    )

    with pytest.raises(UserAlreadyExists):
        await service.create(data)

    db.users.add.assert_not_called()
    db.commit.assert_not_called()


@pytest.mark.asyncio
async def test_create_maps_repository_duplicate_error(service_with_db):
    """
    Test create maps repository duplicate error.

    :param service_with_db: TODO - describe service_with_db.
    :return: None.
    :raises Exception: If the operation fails.
    """
    service, db = service_with_db
    data = UserCreateSchema(email="dup@example.com", password="securepass")
    db.users.get_one_or_none.return_value = None
    db.users.add.side_effect = UserAlreadyExistsRepoException()

    with pytest.raises(UserAlreadyExists):
        await service.create(data)

    db.commit.assert_not_called()


@pytest.mark.asyncio
async def test_update_hashes_password_when_provided(service_with_db):
    """
    Test update hashes password when provided.

    :param service_with_db: TODO - describe service_with_db.
    :return: None.
    :raises Exception: If the operation fails.
    """
    service, db = service_with_db
    update = UserUpdateSchema(password="newsecurepass")
    updated = UserInternalSchema(
        id=3,
        email="user@example.com",
        password="hashed",
        created_at="2025-01-01T00:00:00Z",
        updated_at="2025-01-01T00:00:00Z",
    )
    db.users.update_one.return_value = updated

    result = await service.update(3, update)

    assert result.id == 3
    assert update.password == "hashed::newsecurepass"
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_maps_not_found(service_with_db):
    """
    Test update maps not found.

    :param service_with_db: TODO - describe service_with_db.
    :return: None.
    :raises Exception: If the operation fails.
    """
    service, db = service_with_db
    db.users.update_one.side_effect = UserNotFoundRepoException()

    with pytest.raises(UserNotFound):
        await service.update(100, UserUpdateSchema(email="x@example.com"))

    db.commit.assert_not_called()
