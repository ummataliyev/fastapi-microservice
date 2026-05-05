from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.schemas.base import TimestampSchema, UUIDSchema


class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserUpdateSchema(BaseModel):
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8)


class UserReadSchema(UUIDSchema, TimestampSchema):
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class UserInternalCreateSchema(BaseModel):
    email: EmailStr
    password: str  # already hashed


class UserInternalSchema(UserReadSchema):
    password: str = Field(exclude=True)
