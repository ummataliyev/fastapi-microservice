"""
Integration tests for Complex API endpoints.
"""

import pytest

from src.tests.factories.complex import complex_payload
from src.tests.integration.base.base_crud_test import BaseCRUDTest


@pytest.mark.asyncio
class TestComplexAPI(BaseCRUDTest):
    """
    Integration tests for Complex API endpoints.
    """

    endpoint = "/complexes"
    payload_fn = complex_payload

    @pytest.fixture(autouse=True)
    async def setup(self, ac, clean_db, override_get_db):
        """
        Setup fixture for initializing test data.

        :param ac: AsyncClient instance for making HTTP requests.
        :param clean_db: Fixture to clean the database before tests.
        :param override_get_db: Fixture to override the database dependency.
        """
        self.ac = ac
        self.complex_1 = await self._create_sample(
            name={"en": "Green Valley", "ru": "Зеленая Долина", "uz": "Yashil Vodiy"},
            parking_space_quantity=1,
        )
        self.complex_2 = await self._create_sample(
            name={"en": "Complex B", "ru": "Комплекс Б", "uz": "Majmu B"},
            parking_space_quantity=2,
            status="under_construction",
        )
        self.complex_id_1 = self.complex_1["id"]
        self.complex_id_2 = self.complex_2["id"]

    async def _create_sample(self, name=None, **overrides):
        """
        Create a sample complex using complex_payload.

        :param name: Dictionary containing translated names of the complex.
        :param overrides: Additional fields for the complex payload.
        :return: Created complex data as a dictionary.
        """
        if name is None:
            name = {
                "en": "Sample Complex",
                "ru": "Пример Комплекса",
                "uz": "Namuna Majmu",
            }
        return await self.create_item(self.ac, name=name, **overrides)

    async def test_get_complex(self):
        """
        Test retrieving a single complex by ID.

        :return: Asserts that the retrieved complex matches the expected ID and has a dict `name`.
        """
        data = await self.get_item(self.ac, self.complex_id_1)
        assert data["id"] == self.complex_id_1
        assert isinstance(data["name"], dict)

    async def test_create_complex(self):
        """
        Test creating a new complex.

        :return: Asserts that the created complex has the expected fields.
        """
        created = await self._create_sample(
            name={"en": "New Complex", "ru": "Новый Комплекс", "uz": "Yangi Majmu"},
            parking_space_quantity=5,
            status="active",
        )
        assert created["name"]["en"] == "New Complex"
        assert created["parking_space_quantity"] == 5
        assert created["status"] == "active"

    async def test_update_complex(self):
        """
        Test updating an existing complex.

        :return: Asserts that the updated complex has the new name.
        """
        new_name = {
            "en": "Updated Complex",
            "ru": "Обновленный Комплекс",
            "uz": "Yangilangan Majmu",
        }
        updated = await self.update_item(self.ac, self.complex_id_1, name=new_name)
        assert updated["name"] == new_name

    async def test_delete_complex(self):
        """
        Test deleting a complex.

        :return: Asserts that the deleted complex matches the expected ID.
        """
        deleted = await self.delete_item(self.ac, self.complex_id_2)
        assert deleted["id"] == self.complex_id_2

    async def test_restore_complex(self):
        """
        Test restoring a previously deleted complex.

        :return: Asserts that the restored complex matches the expected ID.
        """
        await self.delete_item(self.ac, self.complex_id_2)
        restored = await self.restore_item(self.ac, self.complex_id_2)
        assert restored["id"] == self.complex_id_2

    async def test_list_complexes(self):
        """
        Test retrieving a list of complexes.

        :return: Asserts that the response contains the created complexes in the list.
        """
        resp = await self.ac.get(f"{self.endpoint}")
        assert resp.status_code == 200
        result = resp.json()
        complexes = result["data"]
        assert isinstance(complexes, list)
        assert any(c["id"] == self.complex_id_1 for c in complexes)
        assert any(c["id"] == self.complex_id_2 for c in complexes)
