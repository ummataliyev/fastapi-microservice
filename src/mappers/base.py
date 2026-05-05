from typing import ClassVar, Generic, TypeVar

from pydantic import BaseModel as PydanticModel

from src.db.sqlalchemy.base import Base

TModel = TypeVar("TModel", bound=Base)
TSchema = TypeVar("TSchema", bound=PydanticModel)


class BaseDataMapper(Generic[TModel, TSchema]):
    model: ClassVar[type[Base]]
    schema: ClassVar[type[PydanticModel]]
    schema_with_rels: ClassVar[type[PydanticModel] | None] = None

    @classmethod
    def map_to_domain_entity(cls, instance: TModel) -> TSchema:
        return cls.schema.model_validate(instance, from_attributes=True)

    @classmethod
    def map_to_domain_entity_with_rels(cls, instance: TModel) -> TSchema:
        target = cls.schema_with_rels or cls.schema
        return target.model_validate(instance, from_attributes=True)

    @classmethod
    def map_to_persistence_entity(cls, schema: TSchema) -> TModel:
        return cls.model(**schema.model_dump(exclude_unset=True))
