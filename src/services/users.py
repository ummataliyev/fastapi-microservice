from uuid import UUID

from fastapi_pagination import Page

from src.managers.db.transaction import TransactionManager
from src.mappers.users import UsersMapper
from src.models.users import Users
from src.schemas.users import (
    UserCreateSchema,
    UserInternalCreateSchema,
    UserReadSchema,
    UserUpdateSchema,
)
from src.security.implementations.bcrypt import bcrypt_hasher
from src.services.base import BaseService


class UsersService(BaseService[TransactionManager]):
    hasher = bcrypt_hasher

    async def list(self) -> Page[UserReadSchema]:
        stmt = self.db.users.list_select().order_by(Users.created_at.desc())
        return await self.paginated_list(
            stmt,
            transformer=lambda rows: [UsersMapper.map_to_domain_entity(r) for r in rows],
        )

    async def get(self, user_id: UUID) -> UserReadSchema:
        return await self.db.users.get_one(user_id)

    async def create(self, data: UserCreateSchema) -> UserReadSchema:
        email = data.email.lower()
        hashed = self.hasher.hash(data.password)
        return await self.db.users.create(
            UserInternalCreateSchema(email=email, password=hashed)
        )

    async def update(self, user_id: UUID, data: UserUpdateSchema) -> UserReadSchema:
        payload = data.model_dump(exclude_unset=True)
        if "password" in payload and payload["password"] is not None:
            payload["password"] = self.hasher.hash(payload["password"])
        if "email" in payload and payload["email"] is not None:
            payload["email"] = payload["email"].lower()
        return await self.db.users.update(user_id, payload)

    async def delete(self, user_id: UUID) -> None:
        await self.db.users.soft_delete(user_id)
