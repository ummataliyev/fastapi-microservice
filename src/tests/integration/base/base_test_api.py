class BaseTestAPI:
    @staticmethod
    async def post(ac, url: str, payload: dict, expected_status: int = 201) -> dict:
        resp = await ac.post(url, json=payload)
        assert resp.status_code == expected_status, resp.json()
        return resp.json()

    @staticmethod
    async def get(ac, url: str, expected_status: int = 200) -> dict:
        resp = await ac.get(url)
        assert resp.status_code == expected_status, resp.json()
        return resp.json()

    @staticmethod
    async def patch(ac, url: str, payload: dict = None, expected_status: int = 200) -> dict:
        resp = await ac.patch(url, json=payload or {})
        assert resp.status_code == expected_status, resp.json()
        return resp.json()

    @staticmethod
    async def delete(ac, url: str, expected_status: int = 200) -> dict:
        resp = await ac.delete(url)
        assert resp.status_code == expected_status, resp.json()
        return resp.json()
