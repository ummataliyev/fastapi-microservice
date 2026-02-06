"""
Service-layer logic for users.
"""

from src.services.base import BaseService

from src.schemas.users import UserReadSchema
from src.schemas.users import UserCreateSchema
from src.schemas.users import UserUpdateSchema
from src.schemas.pagination import PaginatedResponseSchema

from src.exceptions.service.users import UserNotFound
from src.exceptions.service.users import UserAlreadyExists
from src.exceptions.service.users import InvalidUsersInput
from src.exceptions.repository.users import UserNotFoundRepoException
from src.exceptions.repository.users import UserAlreadyExistsRepoException
from src.exceptions.repository.base import InvalidRepositoryInputRepoException

from src.security.implementations.bcrypt_hasher import BcryptPasswordHasher


class UsersService(BaseService):
    """
    Service class for CRUD operations on users with simple integer IDs.
    Only handles email and password fields without any authentication logic.
    """

    password_hasher = BcryptPasswordHasher()

    async def get_one_by_id(self, user_id: int) -> UserReadSchema:
        """
        Get one by id.

        :param user_id: TODO - describe user_id.
        :type user_id: int
        :return: TODO - describe return value.
        :rtype: UserReadSchema
        :raises from_repo: If the operation cannot be completed.
        """
        try:
            user = await self.db.users.get_one(id=user_id)
            return user
        except UserNotFoundRepoException as ex:
            raise UserNotFound.from_repo(ex) from ex

    async def get_by_email(self, email: str) -> UserReadSchema:
        """
        Get by email.

        :param email: TODO - describe email.
        :type email: str
        :return: TODO - describe return value.
        :rtype: UserReadSchema
        :raises from_repo: If the operation cannot be completed.
        """
        try:
            user = await self.db.users.get_one(email=email.lower())
            return user
        except UserNotFoundRepoException as ex:
            raise UserNotFound.from_repo(ex) from ex

    async def get_list(
        self,
        limit: int = 10,
        offset: int = 0,
        current_page: int = 1,
    ) -> PaginatedResponseSchema[UserReadSchema]:
        """
        Get list.

        :param limit: TODO - describe limit.
        :type limit: int
        :param offset: TODO - describe offset.
        :type offset: int
        :param current_page: TODO - describe current_page.
        :type current_page: int
        :return: TODO - describe return value.
        :rtype: PaginatedResponseSchema[UserReadSchema]
        :raises from_repo: If the operation cannot be completed.
        """
        try:
            items = await self.db.users.get_all(
                limit=limit,
                offset=offset,
            )
            total_items = await self.db.users.count()
        except InvalidRepositoryInputRepoException as ex:
            raise InvalidUsersInput.from_repo(ex) from ex

        return self.build_paginated_response(
            items=items,
            total_items=total_items,
            current_page=current_page,
            per_page=limit,
            message="Users retrieved successfully",
        )

    async def create(self, data: UserCreateSchema) -> UserReadSchema:
        """
        Create a new user with a hashed password.
        """
        normalized_email = data.email.lower()
        existing = await self.db.users.get_one_or_none(email=normalized_email)
        if existing:
            raise UserAlreadyExists("User with this email already exists")

        data.email = normalized_email
        data.password = self.password_hasher.hash(data.password)

        try:
            user = await self.db.users.add(data)
            await self.db.commit()
            return user
        except UserAlreadyExistsRepoException as ex:
            raise UserAlreadyExists.from_repo(ex) from ex

    async def update(self, user_id: int, data: UserUpdateSchema) -> UserReadSchema: # noqa
        """
        Update user email or password.
        """
        if data.email is not None:
            data.email = data.email.lower()
        if data.password is not None:
            data.password = self.password_hasher.hash(data.password)

        try:
            user = await self.db.users.update_one(
                id=user_id,
                data=data,
                partially=True
            )
            await self.db.commit()
            return user
        except UserNotFoundRepoException as ex:
            raise UserNotFound.from_repo(ex) from ex

    async def delete(self, user_id: int) -> int:
        """
        Delete user and return the deleted ID.
        """
        try:
            user = await self.db.users.delete_one(id=user_id)
            await self.db.commit()
            return user.id
        except UserNotFoundRepoException as ex:
            raise UserNotFound.from_repo(ex) from ex
