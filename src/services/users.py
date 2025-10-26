from src.services.base import BaseService
from src.schemas.users import (
    UserCreateSchema,
    UserUpdateSchema,
    UserReadSchema,
)
from src.schemas.pagination import PaginatedResponseSchema
from src.exceptions.service.users import (
    UserNotFound,
    UserAlreadyExists,
)
from src.exceptions.repository.users import (
    UserNotFoundRepoException,
    UserAlreadyExistsRepoException,
)


class UsersService(BaseService):
    """
    Service class for CRUD operations on users with simple integer IDs.
    Only handles email and password fields without any authentication logic.
    """

    async def get_one_by_id(self, user_id: int) -> UserReadSchema:
        try:
            user = await self.db.users.get_one(id=user_id)
            return UserReadSchema(**user)
        except UserNotFoundRepoException as ex:
            raise UserNotFound.from_repo(ex)

    async def get_by_email(self, email: str) -> UserReadSchema:
        try:
            user = await self.db.users.get_one(email=email)
            return UserReadSchema(**user)
        except UserNotFoundRepoException as ex:
            raise UserNotFound.from_repo(ex)

    async def get_list(
        self,
        limit: int = 10,
        offset: int = 0,
        search: str | None = None,
    ) -> PaginatedResponseSchema:
        """
        List users with optional search by email.
        """
        items, total = await self.db.users.get_all(
            limit=limit,
            offset=offset,
            search=search,
        )

        return PaginatedResponseSchema(
            users=[UserReadSchema(**i) for i in items],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def create(self, data: UserCreateSchema) -> UserReadSchema:
        """
        Create a new user with plain email & password.
        """
        try:
            existing = await self.db.users.get_one_or_none(email=data.email)
            if existing:
                raise UserAlreadyExists("User with this email already exists")
        except UserAlreadyExistsRepoException as ex:
            raise UserAlreadyExists.from_repo(ex)

        try:
            user = await self.db.users.add(data)
            await self.db.commit()
            return UserReadSchema(**user)
        except UserAlreadyExistsRepoException as ex:
            raise UserAlreadyExists.from_repo(ex)

    async def update(self, user_id: int, data: UserUpdateSchema) -> UserReadSchema:
        """
        Update user email or password.
        """
        try:
            updated_user = await self.db.users.update_one(
                id=user_id, data=data, partially=True
            )
            await self.db.commit()
            return UserReadSchema(**updated_user)
        except UserNotFoundRepoException as ex:
            raise UserNotFound.from_repo(ex)

    async def delete(self, user_id: int) -> int:
        """
        Delete user and return the deleted ID.
        """
        try:
            deleted = await self.db.users.delete_one(id=user_id)
            await self.db.commit()
            return deleted.id
        except UserNotFoundRepoException as ex:
            raise UserNotFound.from_repo(ex)
