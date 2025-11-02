import pytest

from src.tests.factories.users import users_payload
from src.tests.integration.base.base_crud_test import BaseCRUDTest


@pytest.mark.asyncio
class TestUsersAPI(BaseCRUDTest):
    endpoint = "/users"
    payload_fn = users_payload

    @pytest.fixture(autouse=True)
    async def setup(self, ac, clean_db, override_get_db):
        self.ac = ac
        self.user_1 = await self._create_sample(email="user1@example.com")
        self.user_2 = await self._create_sample(email="user2@example.com")
        self.user_id_1 = self.user_1["id"]
        self.user_id_2 = self.user_2["id"]

    async def _create_sample(self, **overrides):
        return await self.create_item(self.ac, **overrides)

    async def test_get_user(self):
        data = await self.get_item(self.ac, self.user_id_1)
        assert data["id"] == self.user_id_1
        assert data["email"] == "user1@example.com"

    async def test_create_user(self):
        created = await self._create_sample(email="newuser@example.com")
        assert created["email"] == "newuser@example.com"

    async def test_update_user(self):
        updated = await self.update_item(
            self.ac, self.user_id_1, email="updated@example.com"
        )
        assert updated["email"] == "updated@example.com"

    async def test_delete_user(self):
        deleted = await self.delete_item(self.ac, self.user_id_2)
        assert deleted["id"] == self.user_id_2

    async def test_list_users(self):
        resp = await self.ac.get(f"{self.endpoint}")
        assert resp.status_code == 200
        result = resp.json()
        users = result["data"]
        assert any(u["id"] == self.user_id_1 for u in users)
        assert any(u["id"] == self.user_id_2 for u in users)
