"""Base for protocol-style security interfaces.

Each interface in this package (e.g. JWTHandler, PasswordHasher) is a
typing.Protocol. New interfaces should follow the same pattern: define a
Protocol and reference it from the matching implementation file.
"""
