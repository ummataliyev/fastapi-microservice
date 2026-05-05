from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UUIDSchema(BaseModel):
    """Mixin: adds a UUID `id` primary key field to the schema."""

    id: UUID = Field(
        description="Unique identifier (UUIDv4).",
        examples=["5b7e0c2a-2c8e-4a1a-9d2f-2bd5e0a9f1a4"],
    )
    model_config = ConfigDict(from_attributes=True)


class TimestampSchema(BaseModel):
    """Mixin: adds `created_at` and `updated_at` timestamps to the schema."""

    created_at: datetime = Field(
        description="ISO-8601 timestamp of record creation (UTC).",
        examples=["2026-05-05T10:30:00Z"],
    )
    updated_at: datetime = Field(
        description="ISO-8601 timestamp of the last update (UTC).",
        examples=["2026-05-05T10:30:00Z"],
    )
    model_config = ConfigDict(from_attributes=True)
