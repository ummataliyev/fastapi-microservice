"""
Unit tests for Building Service layer.
"""

import uuid
import pytest

from unittest.mock import AsyncMock

from src.enums.status import Status

from src.services.building import BuildingService

from src.schemas.building import BuildingReadSchema
from src.schemas.building import BuildingCreateSchema
from src.schemas.building import BuildingUpdateSchema

from src.exceptions.service.building import BuildingNotFound

from src.tests.unit.base.base_crud_test import ServiceTestBase


@pytest.mark.asyncio
class TestBuildingService(ServiceTestBase):
    """
    Concrete tests for BuildingService using the reusable template.
    """

    service_cls = BuildingService
    repo_attr = "building"
    read_schema_cls = BuildingReadSchema
    create_schema_cls = BuildingCreateSchema
    update_schema_cls = BuildingUpdateSchema
    not_found_exc_cls = BuildingNotFound

    default_create_payload = {
        "complex_id": uuid.uuid4(),
        "name": {"en": "Test Building"},
        "status": Status.UNDER_CONSTRUCTION,
    }

    default_update_payload = {
        "name": {"en": "Updated Building"},
        "status": Status.ACTIVE,
    }

    default_read_payload = {
        "complex_id": uuid.uuid4(),
        "name": {"en": "Test Building"},
        "status": Status.ACTIVE,
    }

    async def test_update_success(self):
        """
        Method to test successful update of a building.

        :param: None
        :return: None
        """
        fake_id = uuid.uuid4()
        repo = getattr(self.mock_db, self.repo_attr)
        read_instance = self._make_read_instance(fake_id)
        read_instance.name = {"en": "Updated Building"}

        repo.update_one = AsyncMock(return_value=read_instance)
        repo.get_one = AsyncMock(return_value=read_instance)
        self.mock_db.commit = AsyncMock()

        update_obj = self.update_schema_cls(**self.default_update_payload)

        result = await self.service.update(fake_id, update_obj)
        assert result.id == fake_id
        assert result.name["en"] == "Updated Building"

        repo.update_one.assert_awaited_once_with(id=fake_id, data=update_obj)
        repo.get_one.assert_awaited_once_with(id=fake_id)
        self.mock_db.commit.assert_awaited_once()

    async def test_restore_many_success(self):
        """
        Method to test successful restoration of multiple buildings.

        :param: None
        :return: None
        """
        repo = getattr(self.mock_db, self.repo_attr)
        repo.restore_bulk = AsyncMock(return_value=3)
        self.mock_db.commit = AsyncMock()

        ids = [uuid.uuid4(), uuid.uuid4(), uuid.uuid4()]
        result = await self.service.restore_many(ids=ids)

        assert result == 3
        repo.restore_bulk.assert_awaited_once_with(ids=ids)
        self.mock_db.commit.assert_awaited_once()
