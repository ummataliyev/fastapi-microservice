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
        """
        Create item.

        :param ac: TODO - describe ac.
        :param overrides: TODO - describe overrides.
        :return: TODO - describe return value.
        :raises Exception: If the operation fails.
        """
        return await BaseTestAPI.post(ac, self.endpoint, self.payload_fn(**overrides)) # noqa

    async def get_item(self, ac, item_id):
        """
        Get item.

        :param ac: TODO - describe ac.
        :param item_id: TODO - describe item_id.
        :return: TODO - describe return value.
        :raises Exception: If the operation fails.
        """
        return await BaseTestAPI.get(ac, f"{self.endpoint}/{item_id}")

    async def update_item(self, ac, item_id, **overrides):
        """
        Update item.

        :param ac: TODO - describe ac.
        :param item_id: TODO - describe item_id.
        :param overrides: TODO - describe overrides.
        :return: TODO - describe return value.
        :raises Exception: If the operation fails.
        """
        return await BaseTestAPI.patch(
            ac, f"{self.endpoint}/{item_id}", self.payload_fn(**overrides)
        )

    async def delete_item(self, ac, item_id):
        """
        Delete item.

        :param ac: TODO - describe ac.
        :param item_id: TODO - describe item_id.
        :return: TODO - describe return value.
        :raises Exception: If the operation fails.
        """
        return await BaseTestAPI.delete(ac, f"{self.endpoint}/{item_id}")

    async def restore_item(self, ac, item_id):
        """
        Restore item.

        :param ac: TODO - describe ac.
        :param item_id: TODO - describe item_id.
        :return: TODO - describe return value.
        :raises Exception: If the operation fails.
        """
        return await BaseTestAPI.patch(ac, f"{self.endpoint}/{item_id}/restore") # noqa
