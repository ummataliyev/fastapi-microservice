"""
Repository for User persistence and retrieval.
"""

from sqlalchemy.exc import IntegrityError

from src.models.users import Users
from src.mappers.users import UsersMapper
from src.repositories.base import BaseRepository
from src.exceptions.repository.base import ObjectNotFoundRepoException
from src.exceptions.repository.users import UserNotFoundRepoException
from src.exceptions.repository.users import UserAlreadyExistsRepoException


class UsersRepository(BaseRepository[Users]):
    """
    Repository for managing User persistence and retrieval.
    """

    model = Users
    mapper = UsersMapper

    async def get_one(self, **kwargs):
        """
        Retrieve a single user by filter.
        Raises UserNotFoundRepoException if not found.
        """
        try:
            return await super().get_one(**kwargs)
        except ObjectNotFoundRepoException as ex:
            raise UserNotFoundRepoException from ex

    async def add(self, data):
        """
        Add a new user to the database.
        Raises UserAlreadyExistsRepoException if email already exists.
        """
        try:
            return await super().add(data)
        except IntegrityError as ex:
            raise UserAlreadyExistsRepoException from ex

    async def update_one(self, data, partially: bool = False, **kwargs):
        """
        Update a user.
        Raises UserNotFoundRepoException if not found.
        """
        try:
            return await super().update_one(data, partially=partially, **kwargs)
        except ObjectNotFoundRepoException as ex:
            raise UserNotFoundRepoException from ex

    async def delete_one(self, **kwargs):
        """
        Soft delete a user.
        Raises UserNotFoundRepoException if not found.
        """
        try:
            return await super().delete_one(**kwargs)
        except ObjectNotFoundRepoException as ex:
            raise UserNotFoundRepoException from ex

    async def restore_one(self, **kwargs):
        """
        Restore a soft-deleted user.
        Raises UserNotFoundRepoException if not found or not deleted.
        """
        try:
            return await super().restore_one(**kwargs)
        except ObjectNotFoundRepoException as ex:
            raise UserNotFoundRepoException from ex
