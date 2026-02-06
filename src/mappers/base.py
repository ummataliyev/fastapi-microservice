"""
Base data mapper.
"""

from typing import ClassVar

from pydantic import BaseModel

from src.db.sqlalchemy import Base


class BaseDataMapper:
    """
    Base class for converting between SQLAlchemy models and Pydantic schemas.

    Attributes:
        model (Type[Base]): SQLAlchemy model class to map from/to.
        schema (Type[BaseModel]): Pydantic schema without relations.
        schema_with_rels (Type[BaseModel] | None): Optional schema with relations.
    """

    model: ClassVar[type[Base] | None] = None
    schema: ClassVar[type[BaseModel] | None] = None
    schema_with_rels: ClassVar[type[BaseModel] | None] = None

    @classmethod
    def _ensure_configured(cls) -> None:
        """
         ensure configured.

        :return: None.
        :raises ValueError: If the operation cannot be completed.
        """
        if cls.model is None:
            raise ValueError(f"{cls.__name__}.model is not configured")
        if cls.schema is None:
            raise ValueError(f"{cls.__name__}.schema is not configured")

    @classmethod
    def map_to_domain_entity(
        cls,
        model_instance: Base,
        with_rels: bool = False,
    ) -> BaseModel:
        """
        Convert a SQLAlchemy model instance to a Pydantic schema.

        :param model_instance: SQLAlchemy model instance to be mapped.
        :param with_rels: If True, use schema_with_rels; otherwise use schema.
        :return: A validated Pydantic schema instance.
        """
        cls._ensure_configured()
        schema_to_use = (
            cls.schema_with_rels if with_rels and cls.schema_with_rels else cls.schema
        )
        if schema_to_use is None:
            raise ValueError(f"{cls.__name__}.schema is not configured")
        return schema_to_use.model_validate(
            model_instance,
            from_attributes=True,
        )

    @classmethod
    def map_to_persistence_entity(
        cls,
        schema_instance: BaseModel,
    ) -> Base:
        """
        Convert a Pydantic schema instance to a SQLAlchemy model.

        :param schema_instance: Pydantic schema instance to be mapped.
        :return: A new SQLAlchemy model instance.
        """
        cls._ensure_configured()
        return cls.model(**schema_instance.model_dump())
