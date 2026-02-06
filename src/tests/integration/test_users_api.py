"""
Integration tests for test users api.
"""

import pytest

from src.tests.factories.users import users_payload
from src.tests.integration.base.base_crud_test import BaseCRUDTest


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.postgres
class TestUsersAPI(BaseCRUDTest):
    """
    TestUsersAPI class.
    :raises Exception: If class initialization or usage fails.
    """
    endpoint = "/api/v1/users"
    payload_fn = users_payload

    @pytest.fixture(autouse=True)
    async def setup(self, ac, clean_db, override_get_db):
        """
        Setup.

        :param ac: TODO - describe ac.
        :param clean_db: TODO - describe clean_db.
        :param override_get_db: TODO - describe override_get_db.
        :return: None.
        :raises Exception: If the operation fails.
        """
        self.ac = ac
        self.user_1 = await self._create_sample(email="user1@example.com")
        self.user_2 = await self._create_sample(email="user2@example.com")
        self.user_id_1 = self.user_1["id"]
        self.user_id_2 = self.user_2["id"]

    async def _create_sample(self, **overrides):
        """
         create sample.

        :param overrides: TODO - describe overrides.
        :return: TODO - describe return value.
        :raises Exception: If the operation fails.
        """
        return await self.create_item(self.ac, **overrides)

    async def test_get_user(self):
        """
        Test get user.

        :return: None.
        :raises Exception: If the operation fails.
        """
        data = await self.get_item(self.ac, self.user_id_1)
        assert data["id"] == self.user_id_1
        assert data["email"] == "user1@example.com"

    async def test_create_user(self):
        """
        Test create user.

        :return: None.
        :raises Exception: If the operation fails.
        """
        created = await self._create_sample(email="newuser@example.com")
        assert created["email"] == "newuser@example.com"

    async def test_update_user(self):
        """
        Test update user.

        :return: None.
        :raises Exception: If the operation fails.
        """
        updated = await self.update_item(
            self.ac, self.user_id_1, email="updated@example.com"
        )
        assert updated["email"] == "updated@example.com"

    async def test_delete_user(self):
        """
        Test delete user.

        :return: None.
        :raises Exception: If the operation fails.
        """
        deleted = await self.delete_item(self.ac, self.user_id_2)
        assert deleted["id"] == self.user_id_2

    async def test_list_users(self):
        """
        Test list users.

        :return: None.
        :raises Exception: If the operation fails.
        """
        resp = await self.ac.get(f"{self.endpoint}")
        assert resp.status_code == 200
        result = resp.json()
        users = result["data"]
        assert any(u["id"] == self.user_id_1 for u in users)
        assert any(u["id"] == self.user_id_2 for u in users)
