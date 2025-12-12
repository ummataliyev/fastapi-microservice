"""
Bcrypt password hasher implementation using passlib.
"""

from passlib.context import CryptContext

from src.security.interfaces.hasher import PasswordHasher


class BcryptPasswordHasher(PasswordHasher):
    """
    Password hashing and verification using bcrypt via passlib.

    This class provides methods to hash plain passwords and verify
    them against stored hashed passwords.
    """

    def __init__(self):
        """
        Initialize the password hasher with bcrypt algorithm.
        """
        self._pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
        )

    def hash(self, password: str) -> str:
        """
        Hash a plain text password using bcrypt.

        :param password: Plain text password to hash.
        :return: Hashed password as a string.
        """
        return self._pwd_context.hash(password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain text password against a hashed password.

        :param plain_password: Plain text password to verify.
        :param hashed_password: Hashed password to check against.
        :return: True if the password matches, False otherwise.
        """
        return self._pwd_context.verify(plain_password, hashed_password)
