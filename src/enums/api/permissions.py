"""
Permission codes for this service.

- The enum *value* MUST equal the string the external permission service knows
  (e.g. `EMPLOYEE_LIST = "VI13"`). Do NOT invent codes — every value must be
  whitelisted upstream, otherwise routes return 403.
- The enum *member name* is internal and may be renamed freely.

Add codes for each new endpoint, then reference as
    PermissionChecker(required_permissions=Permission.MY_CODE)
in the route signature.
"""

from enum import StrEnum


class Permission(StrEnum):
    # Add codes here, e.g.:
    # ITEM_LIST = "TPL_ITEM_LIST"
    # ITEM_CREATE = "TPL_ITEM_CREATE"
    pass
