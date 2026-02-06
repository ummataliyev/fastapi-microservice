"""
Integration tests for base test api.
"""


class BaseTestAPI:
    """
    BaseTestAPI class.
    :raises Exception: If class initialization or usage fails.
    """

    @staticmethod
    async def post(
        ac,
        url: str,
        payload: dict,
        expected_status: int = 201
    ) -> dict:
        """
        Post.

        :param ac: TODO - describe ac.
        :param url: TODO - describe url.
        :type url: str
        :param payload: TODO - describe payload.
        :type payload: dict
        :param expected_status: TODO - describe expected_status.
        :type expected_status: int
        :return: TODO - describe return value.
        :rtype: dict
        :raises Exception: If the operation fails.
        """
        resp = await ac.post(url, json=payload)
        assert resp.status_code == expected_status, resp.json()
        return resp.json()

    @staticmethod
    async def get(ac, url: str, expected_status: int = 200) -> dict:
        """
        Get.

        :param ac: TODO - describe ac.
        :param url: TODO - describe url.
        :type url: str
        :param expected_status: TODO - describe expected_status.
        :type expected_status: int
        :return: TODO - describe return value.
        :rtype: dict
        :raises Exception: If the operation fails.
        """
        resp = await ac.get(url)
        assert resp.status_code == expected_status, resp.json()
        return resp.json()

    @staticmethod
    async def patch(
        ac, url: str, payload: dict = None, expected_status: int = 200
    ) -> dict:
        """
        Patch.

        :param ac: TODO - describe ac.
        :param url: TODO - describe url.
        :type url: str
        :param payload: TODO - describe payload.
        :type payload: dict
        :param expected_status: TODO - describe expected_status.
        :type expected_status: int
        :return: TODO - describe return value.
        :rtype: dict
        :raises Exception: If the operation fails.
        """
        resp = await ac.patch(url, json=payload or {})
        assert resp.status_code == expected_status, resp.json()
        return resp.json()

    @staticmethod
    async def delete(ac, url: str, expected_status: int = 200) -> dict:
        """
        Delete.

        :param ac: TODO - describe ac.
        :param url: TODO - describe url.
        :type url: str
        :param expected_status: TODO - describe expected_status.
        :type expected_status: int
        :return: TODO - describe return value.
        :rtype: dict
        :raises Exception: If the operation fails.
        """
        resp = await ac.delete(url)
        assert resp.status_code == expected_status, resp.json()
        return resp.json()
