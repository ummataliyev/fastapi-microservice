"""
Abstract interface for token generation and validation.
"""


from typing import Any
from typing import Dict

from abc import ABC
from abc import abstractmethod


class TokenService(ABC):
    """
    Abstract interface for any token generator and validator.

    This interface defines methods to create access and refresh tokens
    and decode/validate them.
    """

    @abstractmethod
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """
        Create a JWT access token.

        :param data: Dictionary of claims to include in the token.
        :return: Encoded JWT access token as a string.
        :raises NotImplementedError: If not implemented by subclass.
        """
        raise NotImplementedError

    @abstractmethod
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """
        Create a JWT refresh token.

        :param data: Dictionary of claims to include in the token.
        :return: Encoded JWT refresh token as a string.
        :raises NotImplementedError: If not implemented by subclass.
        """
        raise NotImplementedError

    @abstractmethod
    def decode(self, token: str) -> Dict[str, Any]:
        """
        Decode and validate a JWT token.

        :param token: JWT token string to decode.
        :return: Decoded token payload as a dictionary.
        :raises NotImplementedError: If not implemented by subclass.
        """
        raise NotImplementedError
