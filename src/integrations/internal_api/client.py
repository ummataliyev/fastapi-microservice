"""
Internal API client — reference example for authenticated service-to-service
calls against the base/identity service.

It logs in once (OAuth2 password grant), caches the admin bearer token, and
refreshes it before expiry — all inherited from `TokenAuthIntegration`. New
services should copy this module as the starting point for their own clients
and add the endpoint helpers they need (see users.py / branches.py).
"""

from typing import Any

from src.core.settings import settings
from src.integrations.base import TokenAuthIntegration


class InternalApiClient(TokenAuthIntegration):
    login_path = "/base/api/v1/login"

    def __init__(self) -> None:
        super().__init__(
            base_url=settings.base_service_url,
            timeout=settings.integration_timeout,
        )
        self.username = settings.base_service_username
        self.password = settings.base_service_password

    async def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Authenticated GET returning parsed JSON."""
        return await self._get(path, params=params)

    async def post(self, path: str, **kwargs: Any) -> Any:
        """Authenticated POST returning parsed JSON."""
        return await self._post(path, **kwargs)


# Module-level singleton: one cached token shared across the process.
internal_api_client = InternalApiClient()
