# ================================
# src/services/users.py
# ================================

from src.services.base import BaseService
from src.schemas.users import UserReadSchema, UserCreateSchema, UserUpdateSchema
from src.schemas.pagination import PaginatedResponseSchema
from src.exceptions.service.users import UserNotFound, UserAlreadyExists
from src.exceptions.repository.users import UserNotFoundRepoException, UserAlreadyExistsRepoException


class UsersService(BaseService):
    """
    Service layer for users with basic CRUD operations.
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

    async def get_list(self, limit: int = 10, offset: int = 0, current_page: int = 1) -> PaginatedResponseSchema[UserReadSchema]:
        items = await self.db.users.get_all(limit=limit, offset=offset)
        total_items = await self.db.users.count()
        return self.build_paginated_response(
            items=[UserReadSchema(**u) for u in items],
            total_items=total_items,
            current_page=current_page,
            per_page=limit,
            message="Users retrieved successfully"
        )

    async def create(self, data: UserCreateSchema) -> UserReadSchema:
        try:
            existing = await self.db.users.get_one_or_none(email=data.email)
            if existing:
                raise UserAlreadyExists("User with this email already exists")
        except UserAlreadyExistsRepoException as ex:
            raise UserAlreadyExists.from_repo(ex)

        user = await self.db.users.add(data)
        await self.db.commit()
        return UserReadSchema(**user)

    async def update(self, user_id: int, data: UserUpdateSchema) -> UserReadSchema:
        try:
            user = await self.db.users.update_one(id=user_id, data=data, partially=True)
            await self.db.commit()
            return UserReadSchema(**user)
        except UserNotFoundRepoException as ex:
            raise UserNotFound.from_repo(ex)

    async def delete(self, user_id: int) -> int:
        try:
            user = await self.db.users.delete_one(id=user_id)
            await self.db.commit()
            return user.id
        except UserNotFoundRepoException as ex:
            raise UserNotFound.from_repo(ex)
