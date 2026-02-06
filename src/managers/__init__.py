"""
Database and runtime manager exports.
"""

from typing import Any

from importlib import import_module


__all__ = (
    "AuthManager",
    "ReadonlyManager",
    "BaseAsyncManager",
    "TransactionManager",
    "MiddlewareManager",
    "MongoReadonlyManager",
    "BaseTransactionManager",
    "MongoTransactionManager",
    "WebSocketConnectionManager",
)


_EXPORT_MAP = {
    "BaseAsyncManager": "src.managers.base",
    "BaseTransactionManager": "src.managers.base",
    "ReadonlyManager": "src.managers.readonly",
    "TransactionManager": "src.managers.transaction",
    "MongoReadonlyManager": "src.managers.mongo",
    "MongoTransactionManager": "src.managers.mongo",
    "AuthManager": "src.managers.auth",
    "MiddlewareManager": "src.managers.middleware",
    "WebSocketConnectionManager": "src.managers.websocket",
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
