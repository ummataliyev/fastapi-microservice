"""
Database package exports.
"""

from importlib import import_module
from typing import Any

__all__ = (
    "build_readonly_manager",
    "build_transaction_manager",
    "get_db_provider_bundle",
)

_EXPORT_MAP = {
    "build_readonly_manager": "src.db.factory",
    "build_transaction_manager": "src.db.factory",
    "get_db_provider_bundle": "src.db.factory",
}


def __getattr__(name: str) -> Any:
    """
    Resolve exported symbols lazily to avoid circular imports at package import time.

    :param name: Exported attribute name.
    :type name: str
    :return: Resolved exported symbol.
    :rtype: Any
    :raises AttributeError: If the requested name is not an exported symbol.
    """
    module_name = _EXPORT_MAP.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value
