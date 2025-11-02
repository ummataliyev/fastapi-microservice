import pytest
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock
from typing import Any, Optional
from src.exceptions.repository.base import ObjectNotFoundRepoException


class ServiceTestBase:
    """
    Base class for service layer unit tests.
    Provides reusable async tests for CRUD operations.
    """

    service_cls = None
    repo_attr: str = ""
    read_schema_cls = None
    create_schema_cls = None
    update_schema_cls = None
    not_found_exc_cls = None
    default_create_payload: dict = {}
    default_update_payload: dict = {}
    default_read_payload: dict = {}

    def setup_method(self):
        self.mock_db = MagicMock()
        self.service = self.service_cls(db=self.mock_db)

    def _make_read_instance(self, fake_id: Optional[int] = None) -> Any:
        if fake_id is None:
            fake_id = 1
        payload = dict(self.default_read_payload)
        payload.setdefault("id", fake_id)
        payload.setdefault("created_at", datetime.utcnow())
        payload.setdefault("updated_at", datetime.utcnow())
        if self.read_schema_cls:
            return self.read_schema_cls(**payload)
        mock = MagicMock()
        mock.id = fake_id
        return mock

    async def test_create_success(self):
        repo = getattr(self.mock_db, self.repo_attr)
        read_instance = self._make_read_instance()
        repo.add = AsyncMock(return_value=read_instance)
        self.mock_db.commit = AsyncMock()

        create_obj = self.create_schema_cls(**self.default_create_payload) if self.create_schema_cls else self.default_create_payload
        result = await self.service.create(create_obj)

        repo.add.assert_called_once()
        self.mock_db.commit.assert_awaited_once()
        assert result.id == read_instance.id

    async def test_get_one_by_id_success(self):
        fake_id = 1
        repo = getattr(self.mock_db, self.repo_attr)
        repo.get_one = AsyncMock(return_value=self._make_read_instance(fake_id))
        result = await self.service.get_one_by_id(fake_id)
        repo.get_one.assert_called_once_with(id=fake_id)
        assert result.id == fake_id

    async def test_get_one_by_id_not_found(self):
        fake_id = 1
        repo = getattr(self.mock_db, self.repo_attr)
        repo.get_one = AsyncMock(side_effect=ObjectNotFoundRepoException())
        with pytest.raises(self.not_found_exc_cls):
            await self.service.get_one_by_id(fake_id)

    async def test_update_success(self):
        fake_id = 1
        repo = getattr(self.mock_db, self.repo_attr)
        read_instance = self._make_read_instance(fake_id)
        repo.update_one = AsyncMock(return_value=read_instance)
        self.mock_db.commit = AsyncMock()

        update_obj = self.update_schema_cls(**self.default_update_payload) if self.update_schema_cls else self.default_update_payload
        result = await self.service.update(fake_id, update_obj)

        repo.update_one.assert_called_once_with(id=fake_id, data=update_obj, partially=True)
        self.mock_db.commit.assert_awaited_once()
        assert result.id == fake_id

    async def test_delete_success(self):
        fake_id = 1
        repo = getattr(self.mock_db, self.repo_attr)
        repo.delete_one = AsyncMock(return_value=MagicMock(id=fake_id))
        self.mock_db.commit = AsyncMock()

        result = await self.service.delete(fake_id)

        repo.delete_one.assert_called_once_with(id=fake_id)
        self.mock_db.commit.assert_awaited_once()
        assert result == fake_id
