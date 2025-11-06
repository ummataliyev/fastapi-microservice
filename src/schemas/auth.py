"""
Authentication related Pydantic schemas.
"""

from pydantic import Field
from pydantic import EmailStr
from pydantic import BaseModel


class LoginSchema(BaseModel):
    """
    Schema for user login request.
    """
    email: EmailStr
    password: str = Field(..., min_length=6)


class TokenResponseSchema(BaseModel):
    """
    Schema for token response.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenSchema(BaseModel):
    """
    Schema for refresh token request.
    """
    refresh_token: str


class TokenPayloadSchema(BaseModel):
    """
    Schema for decoded JWT token payload.
    """
    sub: int
    email: str
    exp: int
    type: str
