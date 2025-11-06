"""
Authentication related exceptions.
"""


class AuthException(Exception):
    """Base authentication exception."""
    def __init__(self, message: str = "Authentication error"):
        self.message = message
        super().__init__(self.message)


class InvalidCredentials(AuthException):
    """Raised when credentials are invalid."""
    def __init__(self):
        super().__init__("Invalid email or password")


class InvalidToken(AuthException):
    """Raised when token is invalid or expired."""
    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(message)


class TokenExpired(AuthException):
    """Raised when token has expired."""
    def __init__(self):
        super().__init__("Token has expired")


class InvalidTokenType(AuthException):
    """Raised when token type doesn't match expected type."""
    def __init__(self, expected: str, got: str):
        super().__init__(f"Expected {expected} token, got {got}")
