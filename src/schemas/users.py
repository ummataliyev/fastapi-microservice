"""
Schemas for User API endpoints.
"""

from pydantic import Field
from pydantic import EmailStr
from pydantic import BaseModel

from src.schemas.base import UUIDSchema
from src.schemas.base import TimestampSchema


class BaseUserSchema(BaseModel):
    """
    Shared fields for creating and updating users.
    """

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")


class UserCreateSchema(BaseUserSchema):
    """
    Schema for creating a user.
    """

    pass


class UserUpdateSchema(BaseModel):
    email: EmailStr | None = Field(None, description="User email address")
    password: str | None = Field(None, min_length=8, description="User password (min 8 characters)")


class UserReadSchema(UUIDSchema, TimestampSchema, BaseModel):
    """
    Schema returned from the API when reading user data.
    Includes ID and timestamps but excludes sensitive fields like password.
    """

    email: EmailStr = Field(..., description="User email address")

    class Config:
        from_attributes = True


class UserInternalSchema(UserReadSchema):
    """
    Internal schema that includes password for authentication operations.
    Should NEVER be returned directly from API endpoints.
    """

    password: str = Field(..., exclude=True)
