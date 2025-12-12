"""
Password hasher interface.
"""

from abc import ABC
from abc import abstractmethod


class PasswordHasher(ABC):
    """
    Abstract interface for password hashing providers.

    This interface defines the methods required to hash passwords
    and verify plain passwords against hashed values.
    """

    @abstractmethod
    def hash(self, password: str) -> str:
        """
        Hash a plain text password.

        :param password: The plain text password to hash.
        :return: A string representing the hashed password.
        :raises NotImplementedError: If not implemented by subclass.
        """
        raise NotImplementedError

    @abstractmethod
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain text password against a hashed password.

        :param plain_password: The plain text password to verify.
        :param hashed_password: The hashed password to check against.
        :return: True if the plain password matches the hashed password, False otherwise.
        :raises NotImplementedError: If not implemented by subclass.
        """
        raise NotImplementedError
