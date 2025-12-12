"""
AuthManager: handles authentication, JWT creation/verification,
and password hashing using repositories from TransactionManager.
"""

from typing import Optional

from src.models.users import Users

from src.managers.transaction import TransactionManager

from src.exceptions.service.auth import InvalidToken
from src.exceptions.service.users import UserNotFound
from src.exceptions.service.auth import InvalidTokenType

from src.security.implementations.jwt_service import JWTTokenService
from src.security.implementations.bcrypt_hasher import BcryptPasswordHasher


class AuthManager:
    """
    Authentication manager handling login, token creation,
    verification, and user retrieval.
    Works with repositories provided by TransactionManager.
    """

    def __init__(
        self,
        transaction_manager: TransactionManager,
        token_service: Optional[JWTTokenService] = None,
        password_hasher: Optional[BcryptPasswordHasher] = None,
    ):
        """
        Initialize the AuthManager with a transaction manager, token service,
        and password hasher.

        :param transaction_manager: TransactionManager instance providing repositories and session.
        :param token_service: Optional JWTTokenService instance.
        :param password_hasher: Optional BcryptPasswordHasher instance.
        """
        self.tm = transaction_manager
        self.session = transaction_manager.session
        self.token_service = token_service or JWTTokenService()
        self.password_hasher = password_hasher or BcryptPasswordHasher()

    async def verify_password(self, plain: str, hashed: str) -> bool:
        """
        Verify a plain password against a hashed password.

        :param plain: Plain text password to verify.
        :param hashed: Hashed password to compare against.
        :return: True if passwords match, False otherwise.
        """
        return self.password_hasher.verify(plain, hashed)

    async def hash_password(self, plain: str) -> str:
        """
        Hash a plain password using bcrypt.

        :param plain: Plain text password to hash.
        :return: Hashed password as a string.
        """
        return self.password_hasher.hash(plain)

    async def create_tokens(self, user: Users) -> dict:
        """
        Create access and refresh JWT tokens for a user.

        :param user: User instance for which to create tokens.
        :return: Dictionary with 'access_token' and 'refresh_token'.
        """
        payload = {"sub": str(user.id), "email": user.email}
        access_token = self.token_service.create_access_token(payload)
        refresh_token = self.token_service.create_refresh_token(payload)
        return {"access_token": access_token, "refresh_token": refresh_token}

    async def get_current_user(self, token: str) -> Users:
        """
        Decode access token and get the user from TransactionManager.

        :param token: JWT access token string.
        :return: User instance corresponding to the token.
        :raises InvalidToken: If the token is invalid.
        :raises InvalidTokenType: If the token is not an access token.
        :raises UserNotFound: If no user exists for the token's user ID.
        """
        try:
            payload = self.token_service.decode(token)
        except Exception as ex:
            raise InvalidToken(str(ex))

        token_type = payload.get("type")
        if token_type != "access":
            raise InvalidTokenType("Token must be access type")

        user_id = int(payload.get("sub"))
        user = await self.tm.users.get_one(id=user_id)

        if not user:
            raise UserNotFound("User not found")

        return user
