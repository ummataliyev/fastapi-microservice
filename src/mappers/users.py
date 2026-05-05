from src.mappers.base import BaseDataMapper
from src.models.users import Users
from src.schemas.users import UserReadSchema


class UsersMapper(BaseDataMapper[Users, UserReadSchema]):
    model = Users
    schema = UserReadSchema
