"""
Integration tests for Building API endpoints.
"""

import pytest

from src.tests.factories.complex import complex_payload
from src.tests.factories.building import building_payload

from src.tests.integration.base.base_test_api import BaseTestAPI
from src.tests.integration.base.base_crud_test import BaseCRUDTest


@pytest.mark.asyncio
class TestBuildingAPI(BaseCRUDTest):
    """
    Integration tests for Building API endpoints.
    """

    endpoint = "/buildings"
    payload_fn = building_payload

    @pytest.fixture(autouse=True)
    async def setup(self, ac, clean_db, override_get_db):
        """
        Setup fixture for initializing test data.

        :param ac: AsyncClient instance for making HTTP requests.
        :param clean_db: Fixture to clean the database before tests.
        :param override_get_db: Fixture to override the database dependency.
        """
        self.ac = ac
        complex_data = await BaseTestAPI.post(ac, "/complexes", complex_payload())
        self.complex_id = complex_data["id"]

        self.building_1 = await self._create_sample(name={"en": "Building A"})
        self.building_2 = await self._create_sample(name={"en": "Building B"})
        self.building_id_1 = self.building_1["id"]
        self.building_id_2 = self.building_2["id"]

    async def _create_sample(self, name=None, **overrides):
        """
        Helper method to create a sample building.

        :param name: Dictionary containing translated names of the building.
        :param overrides: Additional fields for the building payload.
        :return: Created building data as a dictionary.
        """
        if name is None:
            name = {"en": "Sample Building", "ru": "Пример Здания", "uz": "Namuna Bino"}
        return await self.create_item(
            self.ac, complex_id=self.complex_id, name=name, **overrides
        )

    async def test_get_building(self):
        """
        Test retrieving a single building by ID.

        :return: Asserts that the retrieved building matches the expected ID and has a dict `name`.
        """
        data = await self.get_item(self.ac, self.building_id_1)
        assert data["id"] == self.building_id_1
        assert isinstance(data["name"], dict)

    async def test_list_buildings(self):
        """
        Test retrieving a list of buildings.

        :return: Asserts that the response contains the created buildings in the list.
        """
        resp = await self.ac.get(f"{self.endpoint}")
        assert resp.status_code == 200
        result = resp.json()
        buildings = result["data"]
        assert isinstance(buildings, list)
        assert any(b["id"] == self.building_id_1 for b in buildings)
        assert any(b["id"] == self.building_id_2 for b in buildings)

    async def test_create_building(self):
        """
        Test creating a new building.

        :return: Asserts that the created building has the expected name.
        """
        created = await self._create_sample(name={"en": "New Building"})
        assert created["name"]["en"] == "New Building"

    async def test_update_building(self):
        """
        Test updating an existing building.

        :return: Asserts that the updated building has the new name.
        """
        new_name = {"en": "Updated Building"}
        updated = await self.update_item(
            self.ac, self.building_id_1, name=new_name, complex_id=self.complex_id
        )
        assert updated["name"] == new_name

    async def test_delete_building(self):
        """
        Test deleting a building.

        :return: Asserts that the deleted building matches the expected ID.
        """
        deleted = await self.delete_item(self.ac, self.building_id_2)
        assert deleted["id"] == self.building_id_2

    async def test_restore_building(self):
        """
        Test restoring a previously deleted building.

        :return: Asserts that the restored building matches the expected ID.
        """
        await self.delete_item(self.ac, self.building_id_2)
        restored = await self.restore_item(self.ac, self.building_id_2)
        assert restored["id"] == self.building_id_2
