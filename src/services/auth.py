"""
Authentication service for JWT-based authentication.
"""

from jose import JWTError

from src.services.base import BaseService

from src.core.security import JWTAuth

from src.schemas.auth import LoginSchema
from src.schemas.users import UserReadSchema
from src.schemas.users import UserCreateSchema
from src.schemas.auth import TokenResponseSchema

from src.exceptions.service.auth import InvalidToken
from src.exceptions.service.users import UserNotFound
from src.exceptions.service.auth import InvalidTokenType
from src.exceptions.service.auth import InvalidCredentials
from src.exceptions.service.users import UserAlreadyExists
from src.exceptions.repository.users import UserNotFoundRepoException
from src.exceptions.repository.users import UserAlreadyExistsRepoException


class AuthService(BaseService):
    """
    Service for handling authentication operations.
    """
    token = JWTAuth()

    async def register(self, data: UserCreateSchema) -> TokenResponseSchema:
        """
        Register a new user and return tokens.

        :param data: User registration data.
        :return: Access and refresh tokens.
        """
        existing = await self.db.users.get_one_or_none(email=data.email)
        if existing:
            raise UserAlreadyExists("User with this email already exists")

        hashed_password = self.token.get_password_hash(data.password)

        user_data = UserCreateSchema(
            email=data.email,
            password=hashed_password
        )

        try:
            user = await self.db.users.add(user_data)
            await self.db.commit()
        except UserAlreadyExistsRepoException as ex:
            raise UserAlreadyExists.from_repo(ex)

        return self._generate_tokens(user)

    async def login(self, credentials: LoginSchema) -> TokenResponseSchema:
        """
        Authenticate user and return tokens.

        :param credentials: User login credentials.
        :return: Access and refresh tokens.
        """
        try:
            user = await self.db.users.get_one(email=credentials.email)
        except UserNotFoundRepoException:
            raise InvalidCredentials()

        if not self.token.verify_password(credentials.password, user.password):
            raise InvalidCredentials()

        return self._generate_tokens(user)

    async def refresh_access_token(self, refresh_token: str) -> TokenResponseSchema:
        """
        Generate new access token using refresh token.

        :param refresh_token: Valid refresh token.
        :return: New access and refresh tokens.
        """
        try:
            payload = self.token.decode_token(refresh_token)
        except JWTError:
            raise InvalidToken()

        token_type = payload.get("type")
        if token_type != "refresh":
            raise InvalidTokenType(expected="refresh", got=token_type)

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

        :param token: JWT access token.
        :return: UserReadSchema of the current user.
        """
        try:
            payload = self.token.decode_token(token)
        except JWTError:
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

    def _generate_tokens(self, user: UserReadSchema) -> TokenResponseSchema:
        """
        Generate access and refresh tokens for a user.

        :param user: UserReadSchema object.
        :return: TokenResponseSchema containing access and refresh tokens.
        """
        token_data = {
            "sub": str(user.id),
            "email": user.email
        }

        access_token = self.token.create_access_token(data={**token_data, "type": "access"})
        refresh_token = self.token.create_refresh_token(data={**token_data, "type": "refresh"})

        return TokenResponseSchema(
            access_token=access_token,
            refresh_token=refresh_token
        )
