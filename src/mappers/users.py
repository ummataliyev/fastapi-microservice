from src.models.users import Users

from src.mappers.base import BaseDataMapper

from src.schemas.users import UserReadSchema


class UsersMapper(BaseDataMapper):
    model = Users
    schema = UserReadSchema
