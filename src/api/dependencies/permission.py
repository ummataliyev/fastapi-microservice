from typing import Iterable

from src.api.dependencies.auth import CurrentUserDep
from src.exceptions.services.base import PermissionDeniedError


class PermissionChecker:
    """
    Dependency factory:

        PermissionChecker(required_permissions=Permission.ITEM_LIST)

    Reads `permissions: list[str]` from the JWT payload. Replace with a call to the
    external permission service if your platform centralizes permission lookup.
    """

    def __init__(self, required_permissions: Iterable[str] | str) -> None:
        if isinstance(required_permissions, str):
            self.required = {required_permissions}
        else:
            self.required = set(required_permissions)

    def __call__(self, user: CurrentUserDep) -> None:
        granted = set(user.get("permissions") or [])
        missing = self.required - granted
        if missing:
            raise PermissionDeniedError(f"Missing permissions: {sorted(missing)}")
