"""
Base class for CRUD operation integration tests.
"""

from src.tests.integration.base.base_test_api import BaseTestAPI


class BaseCRUDTest:
    """
    Base class for CRUD operation tests.

    :param endpoint: API endpoint for the resource
    :param payload_fn: Function to generate payloads for create and update operations
    """

    endpoint: str
    payload_fn: callable

    async def create_item(self, ac, **overrides):
        """
        Create a new item.

        :param ac: Async client
        :param overrides: Fields to override in the payload
        :return: Response from the create operation
        """
        payload = self.payload_fn(**overrides)
        return await BaseTestAPI.post(ac, self.endpoint, payload)

    async def get_item(self, ac, item_id):
        """
        Retrieve an item by its ID.

        :param ac: Async client
        :param item_id: ID of the item to retrieve
        :return: Response from the get operation
        """
        return await BaseTestAPI.get(ac, f"{self.endpoint}/{item_id}")

    async def update_item(self, ac, item_id, **overrides):
        """ "
        Update an existing item.

        :param ac: Async client
        :param item_id: ID of the item to update
        :param overrides: Fields to override in the payload
        :return: Response from the update operation
        """
        return await BaseTestAPI.patch(
            ac, f"{self.endpoint}/{item_id}", self.payload_fn(**overrides)
        )

    async def delete_item(self, ac, item_id):
        """
        Delete an item by its ID.

        :param ac: Async client
        :param item_id: ID of the item to delete
        :return: Response from the delete operation
        """
        return await BaseTestAPI.delete(ac, f"{self.endpoint}/{item_id}")

    async def restore_item(self, ac, item_id):
        """
        Restore a deleted item by its ID.

        :param ac: Async client
        :param item_id: ID of the item to restore
        :return: Response from the restore operation
        """
        return await BaseTestAPI.patch(ac, f"{self.endpoint}/{item_id}/restore")
