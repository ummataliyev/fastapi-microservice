"""Base for security implementations.

Each module here implements one interface from `src.security.interfaces`.
Singletons (e.g. `jwt_handler`, `bcrypt_hasher`) are instantiated at the
bottom of each module so callers can import them directly.
"""
