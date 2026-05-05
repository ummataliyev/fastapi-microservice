from typing import ClassVar, Generic, TypeVar
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.sqlalchemy.base import Base
from src.exceptions.repositories.base import EntityNotFoundError
from src.mappers.base import BaseDataMapper

TModel = TypeVar("TModel", bound=Base)
TEntity = TypeVar("TEntity")


class BaseRepository(Generic[TModel, TEntity]):
    """
    Generic CRUD on a SQLAlchemy model + Pydantic mapping via BaseDataMapper.

    Subclasses MUST set:
        model       : SQLAlchemy ORM class
        mapper      : BaseDataMapper subclass
        entity_name : human-readable name for errors

    Custom queries must call self._active_filter(stmt) to apply soft-delete filtering.
    """

    model: ClassVar[type[Base]]
    mapper: ClassVar[type[BaseDataMapper]]
    entity_name: ClassVar[str]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _active_filter(self, stmt: Select) -> Select:
        deleted_at = getattr(self.model, "deleted_at", None)
        if deleted_at is not None:
            stmt = stmt.where(deleted_at.is_(None))
        return stmt

    async def get_one_or_none(self, entity_id: UUID | int) -> TEntity | None:
        stmt = self._active_filter(select(self.model).where(self.model.id == entity_id))
        instance = (await self.session.execute(stmt)).scalar_one_or_none()
        return self.mapper.map_to_domain_entity(instance) if instance else None

    async def get_one(self, entity_id: UUID | int) -> TEntity:
        entity = await self.get_one_or_none(entity_id)
        if entity is None:
            raise EntityNotFoundError(self.entity_name, entity_id)
        return entity

    async def get_all(self, limit: int | None = None, offset: int | None = None) -> list[TEntity]:
        stmt = self._active_filter(select(self.model))
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)
        instances = (await self.session.execute(stmt)).scalars().all()
        return [self.mapper.map_to_domain_entity(i) for i in instances]

    async def create(self, schema) -> TEntity:
        instance = self.mapper.map_to_persistence_entity(schema)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return self.mapper.map_to_domain_entity(instance)

    async def update(self, entity_id: UUID | int, data: dict) -> TEntity:
        stmt = self._active_filter(select(self.model).where(self.model.id == entity_id))
        instance = (await self.session.execute(stmt)).scalar_one_or_none()
        if instance is None:
            raise EntityNotFoundError(self.entity_name, entity_id)
        for key, value in data.items():
            setattr(instance, key, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return self.mapper.map_to_domain_entity(instance)

    async def soft_delete(self, entity_id: UUID | int) -> None:
        from datetime import datetime

        stmt = self._active_filter(select(self.model).where(self.model.id == entity_id))
        instance = (await self.session.execute(stmt)).scalar_one_or_none()
        if instance is None:
            raise EntityNotFoundError(self.entity_name, entity_id)
        if hasattr(instance, "deleted_at"):
            instance.deleted_at = datetime.utcnow()
        else:
            await self.session.delete(instance)
        await self.session.flush()
