"""
Base class for API tests
"""


class BaseTestAPI:
    @staticmethod
    async def post(ac, url: str, payload: dict, expected_status: int = 201) -> dict:
        """
        Method to make POST requests and assert the expected status code.

        :param ac: Async client instance
        :param url: URL to send the POST request to
        :param payload: JSON payload to include in the POST request
        :param expected_status: Expected HTTP status code (default is 201)
        :return: JSON response as a dictionary
        """
        resp = await ac.post(url, json=payload)
        assert resp.status_code == expected_status, resp.json()
        return resp.json()

    @staticmethod
    async def get(ac, url: str, expected_status: int = 200) -> dict:
        """
        Method to make GET requests and assert the expected status code.

        :param ac: Async client instance
        :param url: URL to send the GET request to
        :param expected_status: Expected HTTP status code (default is 200)
        :return: JSON response as a dictionary
        """
        resp = await ac.get(url)
        assert resp.status_code == expected_status, resp.json()
        return resp.json()

    @staticmethod
    async def patch(
        ac, url: str, payload: dict = None, expected_status: int = 200
    ) -> dict:
        """
        Method to make PATCH requests and assert the expected status code.

        :param ac: Async client instance
        :param url: URL to send the PATCH request to
        :param payload: JSON payload to include in the PATCH request (default is None)
        :param expected_status: Expected HTTP status code (default is 200)
        :return: JSON response as a dictionary
        """
        resp = await ac.patch(url, json=payload or {})
        assert resp.status_code == expected_status, resp.json()
        return resp.json()

    @staticmethod
    async def delete(ac, url: str, expected_status: int = 200) -> dict:
        """
        Method to make DELETE requests and assert the expected status code.

        :param ac: Async client instance
        :param url: URL to send the DELETE request to
        :param expected_status: Expected HTTP status code (default is 200)
        :return: JSON response as a dictionary
        """
        resp = await ac.delete(url)
        assert resp.status_code == expected_status, resp.json()
        return resp.json()
