"""
Base class for CRUD operation integration tests.
"""

from src.tests.integration.base.base_test_api import BaseTestAPI


class BaseCRUDTest:
    """
    Base class for CRUD operation tests.
    """

    endpoint: str
    payload_fn: callable

    async def create_item(self, ac, **overrides):
        return await BaseTestAPI.post(ac, self.endpoint, self.payload_fn(**overrides))

    async def get_item(self, ac, item_id):
        return await BaseTestAPI.get(ac, f"{self.endpoint}/{item_id}")

    async def update_item(self, ac, item_id, **overrides):
        return await BaseTestAPI.patch(ac, f"{self.endpoint}/{item_id}", self.payload_fn(**overrides))

    async def delete_item(self, ac, item_id):
        return await BaseTestAPI.delete(ac, f"{self.endpoint}/{item_id}")

    async def restore_item(self, ac, item_id):
        return await BaseTestAPI.patch(ac, f"{self.endpoint}/{item_id}/restore")
