"""
Schemas for Complex API endpoints.
"""

from pydantic import Field
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import ValidationInfo
from pydantic import field_validator

from src.enums.status import Status

from src.schemas.schemas import UUIDSchema
from src.schemas.schemas import TimestampSchema
from src.schemas.validators.mixins import LocalizedFieldMixin
from src.schemas.building import BuildingReadWithCountsSchema


class BaseComplexSchema(LocalizedFieldMixin):
    """
    Common fields shared by create, update, and read schemas for Complex.

    :param name: Localized names of the residential complex (JSON object).
    :param address: Localized address of the residential complex (JSON object).
    :param parking_space_quantity: Number of available parking spaces (>=0).
    :param status: Status of the residential complex.
    :return: Validated complex schema with localized fields.
    """

    model_config = ConfigDict(extra="forbid")

    name: dict | None = Field(
        None,
        description="Localized names of the residential complex (JSON object)",
        json_schema_extra={
            "example": {
                "uz": "Yashil Vodiy",
                "ru": "Зеленая Долина",
                "en": "Green Valley",
            }
        },
    )
    address: dict | None = Field(
        None,
        description="Localized address of the residential complex (JSON object)",
        json_schema_extra={
            "example": {
                "uz": "123 Asosiy ko‘cha",
                "ru": "123 Главная улица",
                "en": "123 Main Street",
            }
        },
    )
    parking_space_quantity: int | None = Field(
        None, ge=0, description="Number of available parking spaces"
    )
    status: Status = Field(..., description="Status of the residential complex")

    @field_validator("name", "address", mode="before")
    @classmethod
    def validate_localized_fields(cls, v, info: ValidationInfo):
        """
        Validate localized fields (`name`, `address`).

        :param v: Value to validate.
        :param info: Field validation info.
        :return: Validated localized field.
        """

        return cls.validate_localized(info.field_name, v)


class ComplexCreateSchema(BaseComplexSchema):
    """
    Schema used when creating a new Complex.

    Inherits all fields from BaseComplexSchema.

    :return: Complex creation schema.
    """


class ComplexUpdateSchema(LocalizedFieldMixin):
    """
    Schema used when updating an existing Complex.

    All fields are optional to allow partial updates.

    :param name: Optional localized names of the complex (JSON object).
    :param address: Optional localized address of the complex (JSON object).
    :param parking_space_quantity: Optional number of available parking spaces.
    :param status: Optional status of the residential complex.
    :return: Complex update schema.
    """

    model_config = ConfigDict(extra="forbid")

    name: dict | None = Field(
        None,
        description="Localized names of the residential complex (JSON object)",
        json_schema_extra={
            "example": {
                "uz": "Yashil Vodiy",
                "ru": "Зеленая Долина",
                "en": "Green Valley",
            }
        },
    )
    address: dict | None = Field(
        None,
        description="Localized address of the residential complex (JSON object)",
        json_schema_extra={
            "example": {
                "uz": "123 Asosiy ko‘cha",
                "ru": "123 Главная улица",
                "en": "123 Main Street",
            }
        },
    )
    parking_space_quantity: int | None = Field(
        None, ge=0, description="Number of available parking spaces"
    )
    status: Status | None = Field(None, description="Status of the residential complex")

    @field_validator("name", "address", mode="before")
    @classmethod
    def validate_localized_fields(cls, v, info: ValidationInfo):
        """
        Validate localized fields if provided.

        :param v: Value to validate.
        :param info: Field validation info.
        :return: Validated localized field or None.
        """

        if v is not None:
            return cls.validate_localized(info.field_name, v)
        return v


class ComplexReadSchema(UUIDSchema, TimestampSchema, BaseComplexSchema):
    """
    Schema used when returning Complex data from the API.

    Combines:
      - UUIDSchema: includes `id`
      - TimestampSchema: includes `created_at`, `updated_at`
      - BaseComplexSchema: core fields

    :return: Complex read schema.
    """


class ComplexBulkRestoreResponseSchema(BaseModel):
    """
    Response schema for bulk restoring Complex entities.

    :param status: Operation status (e.g., "success").
    :param restored: Number of restored complexes.
    :return: Bulk restore response schema.
    """

    status: str
    restored: int


class ComplexReadWithCountsSchema(ComplexReadSchema):
    """
    Schema used when returning Complex data with counts of related entities.

    Includes:
      - building_count
      - section_count
      - apartment_count
    """

    building_count: int = Field(
        ...,
        description="Number of non-deleted buildings in the complex",
        json_schema_extra={"example": 5},
    )
    section_count: int = Field(
        ...,
        description="Number of non-deleted sections in the complex",
        json_schema_extra={"example": 20},
    )
    floor_count: int = Field(
        ...,
        description="Number of non-deleted apartments in the complex",
        json_schema_extra={"example": 200},
    )
    apartment_count: int = Field(
        ...,
        description="Number of non-deleted apartments in the complex",
        json_schema_extra={"example": 200},
    )


class ComplexReadWithRelationsSchema(ComplexReadWithCountsSchema):
    """
    Schema used when returning Complex data with related entities.

    Inherits all fields from ComplexReadSchema.

    :param buildings: List of related buildings.
    :return: Complex schema with related building data.
    """

    buildings: list[BuildingReadWithCountsSchema] = Field(default_factory=list)


class ComplexBulkDeleteResponseSchema(BaseModel):
    status: str
    deleted: int
