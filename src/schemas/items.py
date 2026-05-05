from pydantic import BaseModel, ConfigDict, Field

from src.schemas.base import TimestampSchema, UUIDSchema


class ItemCreateSchema(BaseModel):
    """Payload for creating a new item."""

    name: str = Field(
        min_length=1,
        max_length=255,
        description="Human-readable item name.",
        examples=["Sourdough loaf"],
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Optional long description.",
        examples=["24-hour fermented; baked daily."],
    )
    quantity: int = Field(
        default=0,
        ge=0,
        description="On-hand stock count.",
        examples=[12],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Sourdough loaf",
                "description": "24-hour fermented; baked daily.",
                "quantity": 12,
            }
        }
    )


class ItemUpdateSchema(BaseModel):
    """Partial-update payload — omit fields to leave them unchanged."""

    name: str | None = Field(default=None, min_length=1, max_length=255, examples=["Sourdough loaf v2"])
    description: str | None = Field(default=None, max_length=1000, examples=["Updated recipe."])
    quantity: int | None = Field(default=None, ge=0, examples=[20])

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"quantity": 20}
        }
    )


class ItemReadSchema(UUIDSchema, TimestampSchema):
    """Public item record."""

    name: str = Field(description="Human-readable item name.", examples=["Sourdough loaf"])
    description: str | None = Field(default=None, description="Optional long description.", examples=["24-hour fermented; baked daily."])
    quantity: int = Field(description="On-hand stock count.", examples=[12])

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "5b7e0c2a-2c8e-4a1a-9d2f-2bd5e0a9f1a4",
                "name": "Sourdough loaf",
                "description": "24-hour fermented; baked daily.",
                "quantity": 12,
                "created_at": "2026-05-05T10:30:00Z",
                "updated_at": "2026-05-05T10:30:00Z",
            }
        },
    )
