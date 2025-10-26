"""
Schemas for User API endpoints.
"""

from pydantic import BaseModel, Field, EmailStr
from src.schemas.schemas import UUIDSchema, TimestampSchema


class BaseUserSchema(BaseModel):
    """
    Shared fields for creating and updating users.
    """
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password")


class UserCreateSchema(BaseUserSchema):
    """
    Schema for creating a user.
    """
    pass


class UserUpdateSchema(BaseModel):
    email: EmailStr | None = Field(None, description="User email address")
    password: str | None = Field(None, min_length=6, description="User password")


class UserReadSchema(UUIDSchema, TimestampSchema, BaseModel):
    """
    Schema returned from the API when reading user data.
    Includes ID and timestamps.
    """
    email: EmailStr = Field(..., description="User email address")

    class Config:
        from_attributes = True
