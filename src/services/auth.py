from uuid import UUID

from src.core.settings import settings
from src.exceptions.repositories.base import EntityNotFoundError
from src.exceptions.services.auth import InvalidCredentialsError
from src.exceptions.services.base import AlreadyExistsError, UnauthorizedError
from src.managers.db.transaction import TransactionManager
from src.schemas.auth import LoginSchema, TokenResponseSchema
from src.schemas.users import (
    UserCreateSchema,
    UserInternalCreateSchema,
    UserReadSchema,
)
from src.security.implementations.bcrypt import bcrypt_hasher
from src.security.implementations.jwt import jwt_handler
from src.services.base import BaseService


class AuthService(BaseService[TransactionManager]):
    jwt = jwt_handler
    hasher = bcrypt_hasher

    async def register(self, data: UserCreateSchema) -> TokenResponseSchema:
        email = data.email.lower()
        if await self.db.users.get_by_email(email):
            raise AlreadyExistsError("User with this email already exists")
        hashed = self.hasher.hash(data.password)
        user = await self.db.users.create(
            UserInternalCreateSchema(email=email, password=hashed)
        )
        return self._issue_tokens(user)

    async def login(self, credentials: LoginSchema) -> TokenResponseSchema:
        email = credentials.email.lower()
        internal = await self.db.users.get_internal_by_email(email)
        if internal is None:
            raise InvalidCredentialsError()
        if not self.hasher.verify(credentials.password, internal.password):
            raise InvalidCredentialsError()
        return self._issue_tokens(internal)

    async def refresh(self, refresh_token: str) -> TokenResponseSchema:
        payload = self.jwt.decode(refresh_token)  # raises UnauthorizedError on bad token
        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type")
        sub = payload.get("sub")
        if not sub:
            raise UnauthorizedError("Invalid token payload")
        try:
            user = await self.db.users.get_one(UUID(sub))
        except EntityNotFoundError as exc:
            raise UnauthorizedError("User no longer exists") from exc
        return self._issue_tokens(user)

    def _issue_tokens(self, user: UserReadSchema) -> TokenResponseSchema:
        base = {"sub": str(user.id), "email": user.email}
        access = self.jwt.encode({**base, "type": "access"})
        refresh_minutes = settings.jwt.refresh_token_expire_days * 24 * 60
        refresh = self.jwt.encode(
            {**base, "type": "refresh"},
            expires_delta_minutes=refresh_minutes,
        )
        return TokenResponseSchema(access_token=access, refresh_token=refresh)
