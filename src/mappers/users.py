"""
Mapper for User table
"""

from src.models.users import Users

from src.mappers.base import BaseDataMapper

from src.schemas.users import UserInternalSchema


class UsersMapper(BaseDataMapper):
    model = Users
    schema = UserInternalSchema
