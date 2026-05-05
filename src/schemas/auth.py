from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginSchema(BaseModel):
    """Credentials submitted by an existing user to obtain a token pair."""

    email: EmailStr = Field(
        description="Registered email address. Stored and matched lowercase.",
        examples=["alice@example.com"],
    )
    password: str = Field(
        min_length=8,
        description="Plain-text password (min 8 characters). Sent over TLS only.",
        examples=["hunter2-secure"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "alice@example.com",
                "password": "hunter2-secure",
            }
        }
    )


class RefreshTokenSchema(BaseModel):
    """Body for the refresh-token exchange endpoint."""

    refresh_token: str = Field(
        description="A valid refresh JWT previously issued by `/auth/login` or `/auth/register`.",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            }
        }
    )


class TokenResponseSchema(BaseModel):
    """JWT token pair returned by `/auth/register`, `/auth/login`, `/auth/refresh`."""

    access_token: str = Field(
        description="Short-lived JWT. Pass as `Authorization: Bearer <token>` on protected endpoints.",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    refresh_token: str = Field(
        description="Long-lived JWT used to obtain a fresh access token via `/auth/refresh`.",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    token_type: str = Field(
        default="bearer",
        description="Always `bearer`. Included for OAuth2 client compatibility.",
        examples=["bearer"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
            }
        }
    )
