"""
Base class for CRUD operation unit tests.
"""

import uuid
import pytest

from typing import Any
from typing import List
from typing import Optional

from datetime import datetime

from unittest.mock import MagicMock
from unittest.mock import AsyncMock

from src.exceptions.repository.base import ObjectNotFoundRepoException


class ServiceTestBase:
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
        """
        Initialize a mock DB and service instance.

        :return: None
        """
        self.mock_db = MagicMock()
        self.service = self.service_cls(db=self.mock_db)

    def _make_read_instance(self, fake_id: Optional[uuid.UUID] = None) -> Any:
        """
        Build a read-schema instance or fallback MagicMock.

        :param fake_id: optional UUID to set on the instance
        :return: either an instance of read_schema_cls or a MagicMock
        """
        if fake_id is None:
            fake_id = uuid.uuid4()
        payload = dict(self.default_read_payload)
        payload.setdefault("id", fake_id)
        payload.setdefault("created_at", datetime.utcnow())
        payload.setdefault("updated_at", datetime.utcnow())
        if self.read_schema_cls is not None:
            return self.read_schema_cls(**payload)
        mock = MagicMock()
        mock.id = fake_id
        return mock

    async def test_create_success(self):
        """
        Ensure service.create calls repository.add and commits.

        :return: None
        """
        repo = getattr(self.mock_db, self.repo_attr)
        read_instance = self._make_read_instance()
        repo.add = AsyncMock(return_value=read_instance)
        self.mock_db.commit = AsyncMock()

        if self.create_schema_cls is not None:
            create_obj = self.create_schema_cls(**self.default_create_payload)
        else:
            create_obj = self.default_create_payload

        result = await self.service.create(create_obj)

        repo.add.assert_called_once()
        self.mock_db.commit.assert_awaited_once()
        if hasattr(result, "id"):
            assert result.id == read_instance.id

    async def test_get_one_by_id_success(self):
        """
        Ensure service.get_one_by_id fetches with repository.get_one(with_rels=True).

        :return: None
        """
        fake_id = uuid.uuid4()
        repo = getattr(self.mock_db, self.repo_attr)
        repo.get_one = AsyncMock(return_value=self._make_read_instance(fake_id))
        result = await self.service.get_one_by_id(fake_id)
        repo.get_one.assert_called_once_with(id=fake_id, with_rels=True)
        if hasattr(result, "id"):
            assert result.id == fake_id

    async def test_get_one_by_id_not_found(self):
        """
        Ensure service raises the service-level not_found exception when repo doesn't find object.

        :return: None
        """
        fake_id = uuid.uuid4()
        repo = getattr(self.mock_db, self.repo_attr)
        repo.get_one = AsyncMock(side_effect=ObjectNotFoundRepoException())
        with pytest.raises(self.not_found_exc_cls):
            await self.service.get_one_by_id(fake_id)

    async def test_update_success(self):
        """
        Ensure service.update calls repository.update_one and commits.

        :return: None
        """
        fake_id = uuid.uuid4()
        repo = getattr(self.mock_db, self.repo_attr)
        read_instance = self._make_read_instance(fake_id)
        repo.update_one = AsyncMock(return_value=read_instance)
        self.mock_db.commit = AsyncMock()

        if self.update_schema_cls is not None:
            update_obj = self.update_schema_cls(**self.default_update_payload)
        else:
            update_obj = self.default_update_payload

        result = await self.service.update(fake_id, update_obj)

        repo.update_one.assert_called_once_with(id=fake_id, data=update_obj)
        self.mock_db.commit.assert_awaited_once()
        if hasattr(result, "id"):
            assert result.id == fake_id

    async def test_delete_success(self):
        """
        Ensure service.delete calls repository.delete_one and commits.

        :return: None
        """
        fake_id = uuid.uuid4()
        repo = getattr(self.mock_db, self.repo_attr)
        repo.delete_one = AsyncMock(return_value=MagicMock(id=fake_id))
        self.mock_db.commit = AsyncMock()

        result = await self.service.delete(fake_id)

        repo.delete_one.assert_called_once_with(id=fake_id)
        self.mock_db.commit.assert_awaited_once()
        assert result == fake_id

    async def test_restore_many_success(self):
        """
        Ensure service.restore_many calls repository.restore_bulk and commits.

        :return: None
        """
        repo = getattr(self.mock_db, self.repo_attr)
        repo.restore_bulk = AsyncMock(return_value=3)
        self.mock_db.commit = AsyncMock()

        ids: List[uuid.UUID] = [uuid.uuid4(), uuid.uuid4(), uuid.uuid4()]
        result = await self.service.restore_many(ids)

        repo.restore_bulk.assert_called_once()
        self.mock_db.commit.assert_awaited_once()
        assert result == 3
