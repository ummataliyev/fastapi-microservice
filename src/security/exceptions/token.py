"""
Eceptions related to token operations.
"""


class TokenError(Exception):
    """
    Base exception for token-related failures.
    """


class TokenDecodeError(TokenError):
    """
    Raised when token decoding/validation fails.
    """


class TokenExpiredError(TokenDecodeError):
    """
    Raised when the token has expired.
    """


class InvalidTokenError(TokenDecodeError):
    """
    Raised when the token is malformed or invalid.
    """
