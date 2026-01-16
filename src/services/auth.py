"""
Authentication service for user registration, login, and token management.
"""

from src.services.base import BaseService

from src.schemas.auth import LoginSchema
from src.schemas.users import UserReadSchema
from src.schemas.users import UserCreateSchema
from src.schemas.users import UserInternalSchema
from src.schemas.auth import TokenResponseSchema

from src.exceptions.service.auth import InvalidToken
from src.exceptions.service.users import UserNotFound
from src.exceptions.service.auth import InvalidTokenType
from src.exceptions.service.auth import InvalidCredentials
from src.exceptions.service.users import UserAlreadyExists
from src.exceptions.repository.users import UserNotFoundRepoException
from src.exceptions.repository.users import UserAlreadyExistsRepoException

from src.security.implementations.jwt_service import JWTTokenService
from src.security.implementations.bcrypt_hasher import BcryptPasswordHasher


class AuthService(BaseService):
    """
    Service for handling authentication operations.

    Attributes:
        token_service (JWTTokenService): Service for creating and verifying JWT tokens.
        password_hasher (BcryptPasswordHasher): Service for hashing and verifying passwords.
    """

    token_service = JWTTokenService()
    password_hasher = BcryptPasswordHasher()

    async def register(self, data: UserCreateSchema) -> TokenResponseSchema:
        """
        Register a new user and return tokens.

        :param data: UserCreateSchema object containing user email and password.
        :type data: UserCreateSchema
        :return: TokenResponseSchema containing access and refresh tokens.
        :rtype: TokenResponseSchema
        :raises UserAlreadyExists: If a user with the given email already exists.
        """
        existing = await self.db.users.get_one_or_none(email=data.email)
        if existing:
            raise UserAlreadyExists("User with this email already exists")

        hashed_password = self.password_hasher.hash(data.password)
        user_data = UserCreateSchema(email=data.email, password=hashed_password)

        try:
            user = await self.db.users.add(user_data)
            await self.db.commit()
        except UserAlreadyExistsRepoException as ex:
            raise UserAlreadyExists.from_repo(ex)

        return self._generate_tokens(user)

    async def login(self, credentials: LoginSchema) -> TokenResponseSchema:
        """
        Authenticate user and return tokens.

        :param credentials: LoginSchema containing email and password.
        :type credentials: LoginSchema
        :return: TokenResponseSchema containing access and refresh tokens.
        :rtype: TokenResponseSchema
        :raises InvalidCredentials: If the email does not exist or password is incorrect.
        """
        try:
            user = await self.db.users.get_one(email=credentials.email)
        except UserNotFoundRepoException:
            raise InvalidCredentials()

        if not self.password_hasher.verify(credentials.password, user.password):
            raise InvalidCredentials()

        return self._generate_tokens(user)

    async def refresh_access_token(self, refresh_token: str) -> TokenResponseSchema:
        """
        Generate a new access token using a refresh token.

        :param refresh_token: Refresh token string.
        :type refresh_token: str
        :return: TokenResponseSchema containing new access and refresh tokens.
        :rtype: TokenResponseSchema
        :raises InvalidToken: If the token is invalid or cannot be decoded.
        :raises InvalidTokenType: If the token type is not "refresh".
        :raises UserNotFound: If the user specified in the token does not exist.
        """
        try:
            payload = self.token_service.decode(refresh_token)
        except Exception:
            raise InvalidToken()

        if payload.get("type") != "refresh":
            raise InvalidTokenType(expected="refresh", got=payload.get("type"))

        user_id = payload.get("sub")
        if not user_id:
            raise InvalidToken("Invalid token payload")

        try:
            user = await self.db.users.get_one(id=user_id)
        except UserNotFoundRepoException:
            raise UserNotFound("User not found")

        return self._generate_tokens(user)

    async def get_current_user(self, token: str) -> UserReadSchema:
        """
        Retrieve the current user from an access token.

        :param token: Access token string.
        :type token: str
        :return: UserReadSchema representing the current authenticated user.
        :rtype: UserReadSchema
        :raises InvalidToken: If the token is invalid or cannot be decoded.
        :raises InvalidTokenType: If the token type is not "access".
        :raises UserNotFound: If the user specified in the token does not exist.
        """
        try:
            payload = self.token_service.decode(token)
        except Exception:
            raise InvalidToken()

        if payload.get("type") != "access":
            raise InvalidTokenType(expected="access", got=payload.get("type"))

        try:
            user_id = int(payload.get("sub"))
        except (ValueError, TypeError):
            raise InvalidToken("Invalid user id in token")

        try:
            user = await self.db.users.get_one(id=user_id)
        except UserNotFoundRepoException:
            raise UserNotFound("User not found")

        return user

    def _generate_tokens(self, user: UserInternalSchema) -> TokenResponseSchema:
        """
        Generate access and refresh tokens for a user.

        :param user: UserInternalSchema object representing the user.
        :type user: UserInternalSchema
        :return: TokenResponseSchema containing access and refresh tokens.
        :rtype: TokenResponseSchema
        """
        token_data = {"sub": str(user.id), "email": user.email}

        access_token = self.token_service.create_access_token(data={**token_data})
        refresh_token = self.token_service.create_refresh_token(data={**token_data})

        return TokenResponseSchema(access_token=access_token, refresh_token=refresh_token)
