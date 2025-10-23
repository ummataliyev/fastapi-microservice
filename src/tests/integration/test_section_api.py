"""
Integration tests for Section API endpoints.
"""

import pytest

from src.tests.factories.section import section_payload
from src.tests.factories.complex import complex_payload
from src.tests.factories.building import building_payload

from src.tests.integration.base.base_test_api import BaseTestAPI
from src.tests.integration.base.base_crud_test import BaseCRUDTest


@pytest.mark.asyncio
class TestSectionAPI(BaseCRUDTest):
    """
    Integration tests for Section API endpoints.
    """

    endpoint = "/sections"
    payload_fn = section_payload

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
        building_data = await BaseTestAPI.post(
            ac, "/buildings", building_payload(complex_id=self.complex_id)
        )
        self.building_id = building_data["id"]

        self.section_1 = await self._create_sample(name={"en": "Section A"})
        self.section_2 = await self._create_sample(name={"en": "Section B"})
        self.section_id_1 = self.section_1["id"]
        self.section_id_2 = self.section_2["id"]

    async def _create_sample(self, name=None, **overrides):
        """
        Helper method to create a sample section.

        :param name: Dictionary containing translated names of the section.
        :param overrides: Additional fields for the section payload.
        :return: Created section data as a dictionary.
        """
        if name is None:
            name = {
                "en": "Sample Section",
                "ru": "Пример Секции",
                "uz": "Namuna Sektsiya",
            }
        return await self.create_item(
            self.ac, building_id=self.building_id, name=name, **overrides
        )

    async def test_get_section(self):
        """
        Test retrieving a single section by ID.

        :return: Asserts that the retrieved section matches the expected ID and has a dict `name`.
        """
        data = await self.get_item(self.ac, self.section_id_1)
        assert data["id"] == self.section_id_1
        assert isinstance(data["name"], dict)

    async def test_list_sections(self):
        """
        Test retrieving a list of sections.

        :return: Asserts that the response contains the created sections in the list.
        """
        resp = await self.ac.get(f"{self.endpoint}")
        assert resp.status_code == 200
        result = resp.json()
        sections = result["data"]
        assert isinstance(sections, list)
        assert any(s["id"] == self.section_id_1 for s in sections)
        assert any(s["id"] == self.section_id_2 for s in sections)

    async def test_create_section(self):
        """
        Test creating a new section.

        :return: Asserts that the created section has the expected name.
        """
        created = await self._create_sample(name={"en": "New Section"})
        assert created["name"]["en"] == "New Section"

    async def test_update_section(self):
        """
        Test updating an existing section.

        :return: Asserts that the updated section has the new name.
        """
        new_name = {"en": "Updated Section"}
        updated = await self.update_item(
            self.ac, self.section_id_1, name=new_name, building_id=self.building_id
        )
        assert updated["name"] == new_name

    async def test_delete_section(self):
        """
        Test deleting a section.

        :return: Asserts that the deleted section matches the expected ID.
        """
        deleted = await self.delete_item(self.ac, self.section_id_2)
        assert deleted["id"] == self.section_id_2

    async def test_restore_section(self):
        """
        Test restoring a previously deleted section.

        :return: Asserts that the restored section matches the expected ID.
        """
        await self.delete_item(self.ac, self.section_id_2)
        restored = await self.restore_item(self.ac, self.section_id_2)
        assert restored["id"] == self.section_id_2
