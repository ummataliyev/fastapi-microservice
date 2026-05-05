from sqlalchemy import select

from src.mappers.users import UsersMapper
from src.models.users import Users
from src.repositories.base import BaseRepository
from src.schemas.users import UserInternalSchema, UserReadSchema


class UsersRepository(BaseRepository[Users, UserReadSchema]):
    model = Users
    mapper = UsersMapper
    entity_name = "User"

    async def get_by_email(self, email: str) -> UserReadSchema | None:
        stmt = self._active_filter(select(Users).where(Users.email == email))
        instance = (await self.session.execute(stmt)).scalar_one_or_none()
        return self.mapper.map_to_domain_entity(instance) if instance else None

    async def get_internal_by_email(self, email: str) -> UserInternalSchema | None:
        stmt = self._active_filter(select(Users).where(Users.email == email))
        instance = (await self.session.execute(stmt)).scalar_one_or_none()
        if instance is None:
            return None
        return UserInternalSchema.model_validate(instance, from_attributes=True)

    def list_select(self):
        """Public Select for pagination — applies the soft-delete filter."""
        return self._active_filter(select(Users))
