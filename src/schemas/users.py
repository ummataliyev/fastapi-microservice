from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.schemas.base import TimestampSchema, UUIDSchema


class UserCreateSchema(BaseModel):
    """Payload for creating a new user (also used by `/auth/register`)."""

    email: EmailStr = Field(
        description="Email address used as the login identifier. Will be stored lowercase.",
        examples=["alice@example.com"],
    )
    password: str = Field(
        min_length=8,
        description="Plain-text password (min 8 characters). Hashed with bcrypt before storage.",
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


class UserUpdateSchema(BaseModel):
    """Partial-update payload. Omitted fields are left unchanged."""

    email: EmailStr | None = Field(
        default=None,
        description="New email address. Stored lowercase. Omit to keep current.",
        examples=["alice.new@example.com"],
    )
    password: str | None = Field(
        default=None,
        min_length=8,
        description="New plain-text password (min 8 chars). Omit to keep current.",
        examples=["new-strong-password"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "alice.new@example.com",
            }
        }
    )


class UserReadSchema(UUIDSchema, TimestampSchema):
    """Public user view returned from API endpoints. Never includes the password."""

    email: EmailStr = Field(
        description="User email address (lowercased).",
        examples=["alice@example.com"],
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "5b7e0c2a-2c8e-4a1a-9d2f-2bd5e0a9f1a4",
                "email": "alice@example.com",
                "created_at": "2026-05-05T10:30:00Z",
                "updated_at": "2026-05-05T10:30:00Z",
            }
        },
    )


class UserInternalCreateSchema(BaseModel):
    """Service-only schema for inserting a user with an already-hashed password.

    Never accept this from API input — it bypasses password validation and
    expects the bcrypt hash directly. Used internally by `AuthService.register`.
    """

    email: EmailStr = Field(description="Lowercased email address.")
    password: str = Field(description="Pre-hashed (bcrypt) password.")


class UserInternalSchema(UserReadSchema):
    """Service-only schema that includes the password hash for verification.

    NEVER returned from a router — `password` is excluded from JSON output via
    `Field(exclude=True)` as a defense-in-depth fallback.
    """

    password: str = Field(exclude=True)
