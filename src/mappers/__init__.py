"""
Mapper-layer exports.
"""

from typing import Any

from importlib import import_module


__all__ = (
    "BaseDataMapper",
    "UsersMapper",
)


_EXPORT_MAP = {
    "BaseDataMapper": "src.mappers.base",
    "UsersMapper": "src.mappers.users",
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
