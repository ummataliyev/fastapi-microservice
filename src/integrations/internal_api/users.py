"""
Base-service `users` API helpers.

The base-service `users` endpoint returns a user record that includes
`branches[]` (branch memberships). These helpers show the common shapes:
single fetch (404 -> None), client-side pagination, and predicate filtering.
"""

from typing import Any
from uuid import UUID

from src.core.observability.logging import get_logger
from src.exceptions.integrations.base import UpstreamResponseError
from src.integrations.internal_api.client import internal_api_client

logger = get_logger(__name__)


async def get_user_by_id(user_id: UUID) -> dict[str, Any] | None:
    """Fetch a single base-service user by id; returns None on 404."""
    try:
        return await internal_api_client.get(f"/base/api/v1/users/{user_id}")
    except UpstreamResponseError as exc:
        if exc.upstream_status == 404:
            return None
        raise


async def find_users_by_job_name(job_name: str) -> list[dict[str, Any]]:
    """Return all base-service users whose `job_name` equals `job_name`.

    Pages through the paginated endpoint until exhausted. An upstream outage
    propagates (it must not be silently reported as "no users found").
    """
    users: list[dict[str, Any]] = []
    page = 1
    size = 100

    while True:
        payload = await internal_api_client.get(
            "/base/api/v1/users",
            params={"page": page, "size": size, "job_name": job_name},
        )
        items = payload.get("items") if isinstance(payload, dict) else payload
        if not items:
            break
        users.extend(items)
        if len(items) < size:
            break
        page += 1

    return users


async def find_users_for_branch(
    branch_id: UUID, *, job_name: str
) -> list[dict[str, Any]]:
    """Return users with `job_name` whose `branches[]` contains `branch_id`.

    The endpoint cannot filter by branch, so we fetch by job_name and filter
    client-side.
    """
    candidates = await find_users_by_job_name(job_name)
    return [u for u in candidates if is_user_in_branch(u, branch_id)]


def is_user_in_branch(user: dict[str, Any], branch_id: UUID) -> bool:
    """Check whether a base-service user record covers `branch_id`."""
    target = str(branch_id)
    for entry in user.get("branches") or []:
        branch = entry.get("branch") if isinstance(entry, dict) else None
        bid = (branch or {}).get("id")
        if bid and str(bid) == target:
            return True
    return False
