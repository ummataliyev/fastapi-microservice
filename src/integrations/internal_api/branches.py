"""Base-service `iiko/branches` API helpers."""

from typing import Any
from uuid import UUID

from src.core.observability.logging import get_logger
from src.exceptions.integrations.base import UpstreamResponseError
from src.integrations.internal_api.client import internal_api_client

logger = get_logger(__name__)


async def list_branch_ids_for_country(country_id: UUID) -> list[UUID]:
    """Branch ids belonging to a country, via base-service.

    base-service returns ``{"items": [{"id", "name", ...}], ...}``;
    ``pagination=false`` returns every branch in one page. Errors propagate —
    an upstream outage must not be masked as "country has no branches".
    """
    data = await internal_api_client.get(
        "/base/api/v1/iiko/branches",
        params={"country_id": str(country_id), "pagination": False},
    )
    items = data.get("items", []) if isinstance(data, dict) else (data or [])
    return [UUID(str(b["id"])) for b in items if b.get("id")]


async def get_branch_by_id(branch_id: UUID) -> dict[str, Any] | None:
    """Fetch a single iiko branch by id; returns None on 404."""
    try:
        return await internal_api_client.get(f"/base/api/v1/iiko/branches/{branch_id}")
    except UpstreamResponseError as exc:
        if exc.upstream_status == 404:
            return None
        raise


async def get_branch_name(branch_id: UUID) -> str | None:
    """Convenience: just the branch name, or None if unavailable."""
    branch = await get_branch_by_id(branch_id)
    return branch.get("name") if branch else None
