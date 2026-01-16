"""
Base Repository methods.
"""

from typing import Any
from typing import TypeVar
from typing import Generic
from typing import Iterable

from pydantic import BaseModel

from sqlalchemy import func
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.postgres import Base
from src.mappers.base import BaseDataMapper
from src.exceptions.repository.base import ObjectNotFoundRepoException
from src.exceptions.repository.base import CannotAddObjectRepoException


T = TypeVar("T")


class BaseRepository(Generic[T]):
    """
    Base repository providing generic CRUD operations for SQLAlchemy models.
    """

    model: type[Base] = None
    mapper: type[BaseDataMapper] = None

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with an async SQLAlchemy session.

        :param session: AsyncSession instance for DB operations.
        """

        self.session = session

    def _active_filter(self, query):
        """
        Apply `deleted_at IS NULL` filter for the primary entity if available.

        :param query: SQLAlchemy query object.
        :return: Query with active filter applied.
        """

        if hasattr(self.model, "deleted_at"):
            query = query.where(self.model.deleted_at.is_(None))
        return query

    def _with_active_children(self, query):
        """
        Apply `deleted_at IS NULL` filter to all child relationships
        that support soft deletion.

        :param query: SQLAlchemy query object.
        :return: Query with child filters applied.
        """

        if hasattr(self.model, "__mapper__"):
            for rel in self.model.__mapper__.relationships:
                child_model = rel.mapper.class_
                if hasattr(child_model, "deleted_at"):
                    query = query.options(
                        with_loader_criteria(
                            child_model, child_model.deleted_at.is_(None)
                        )
                    )
        return query

    async def get_one(
        self, query_options: Iterable = None, with_rels: bool = False, **filter_by
    ) -> T:
        """
        Retrieve a single object matching the filter.

        :param query_options: Optional SQLAlchemy loader options.
        :param with_rels: Whether to include related entities with active filter applied.
        :param filter_by: Field-based filters (e.g., id=uuid).
        :return: Domain entity mapped object.
        :raises ObjectNotFoundRepoException: If no matching object is found.
        """

        query = select(self.model).filter_by(**filter_by)
        query = self._active_filter(query)

        if with_rels:
            query = self._with_active_children(query)

        if query_options:
            query = query.options(*query_options)

        result = await self.session.execute(query)
        try:
            model = result.scalar_one()
        except NoResultFound as ex:
            raise ObjectNotFoundRepoException from ex

        return self.mapper.map_to_domain_entity(model, with_rels=with_rels)

    async def get_all(
        self,
        limit: int = 10,
        offset: int = 0,
        with_rels: bool = False,
        search: str | None = None,
        **filter_by,
    ) -> list[T]:
        """
        Retrieve a paginated list of objects.

        :param limit: Maximum number of records to return.
        :param offset: Number of records to skip before returning results.
        :param with_rels: Whether to include related entities with active filter applied.
        :param search: Optional search term applied to JSONB fields (uz/ru/en).
        :param filter_by: Field-based filters for narrowing results.
        :return: List of domain entities mapped from model instances.
        """

        if limit < 0 or offset < 0:
            raise ValueError("Limit and offset must be non-negative.")

        query = select(self.model).limit(limit).offset(offset)
        query = self._active_filter(query)

        if filter_by:
            query = query.filter_by(**filter_by)

        if with_rels:
            query = self._with_active_children(query)

        result = await self.session.execute(query)
        return [
            self.mapper.map_to_domain_entity(m, with_rels=with_rels)
            for m in result.scalars().all()
        ]

    async def get_one_or_none(self, **filter_by) -> T | None:
        """
        Retrieve a single object matching the filter, or return None.

        :param filter_by: Field-based filters.
        :return: Domain entity or None if no match.
        """

        query = select(self.model).filter_by(**filter_by)
        query = self._active_filter(query)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self.mapper.map_to_domain_entity(model)

    async def add(self, data: BaseModel) -> T:
        """
        Add a single object to the database.

        :param data: Pydantic model containing the data.
        :return: Domain entity of the newly added object.
        :raises CannotAddObjectRepoException: If integrity constraint fails.
        """

        stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        try:
            result = await self.session.execute(stmt)
            model = result.scalar_one()
        except IntegrityError as ex:
            raise CannotAddObjectRepoException from ex
        return self.mapper.map_to_domain_entity(model)

    async def add_bulk(self, data: list[BaseModel]) -> None:
        """
        Add multiple objects to the database at once.

        :param data: List of Pydantic models.
        :raises CannotAddObjectRepoException: If integrity constraint fails.
        """

        stmt = insert(self.model).values([item.model_dump() for item in data])
        try:
            await self.session.execute(stmt)
        except IntegrityError as ex:
            raise CannotAddObjectRepoException from ex

    async def update_one(
        self, data: BaseModel, partially: bool = False, **filter_by
    ) -> T:
        """
        Update a single object.

        :param data: Pydantic model containing updated fields.
        :param partially: If True, only update the fields set in the model.
        :param filter_by: Field-based filters to locate the object.
        :return: Updated domain entity.
        :raises ObjectNotFoundRepoException: If object does not exist.
        """

        stmt = (
            update(self.model)
            .values(**data.model_dump(exclude_unset=partially))
            .filter_by(**filter_by)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        try:
            model = result.scalar_one()
        except NoResultFound as ex:
            raise ObjectNotFoundRepoException from ex
        return self.mapper.map_to_domain_entity(model)

    async def delete_one(self, **filter_by) -> T:
        """
        Soft-delete a single object by setting `deleted_at` timestamp.

        :param filter_by: Field-based filters to locate the object.
        :return: Deleted domain entity.
        :raises ObjectNotFoundRepoException: If object does not exist.
        """

        stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .where(self.model.deleted_at.is_(None))
            .values(deleted_at=func.now())
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise ObjectNotFoundRepoException
        return self.mapper.map_to_domain_entity(model)

    async def delete_bulk(self, list_ids: list[Any]) -> int:
        """
        Soft-delete multiple objects by setting `deleted_at`.

        :param list_ids: List of IDs to delete.
        :return: Number of deleted rows.
        """

        stmt = (
            update(self.model)
            .where(self.model.id.in_(list_ids))
            .where(self.model.deleted_at.is_(None))
            .values(deleted_at=func.now())
        )
        result = await self.session.execute(stmt)
        return result.rowcount or 0

    async def restore_one(self, **filter_by) -> T:
        """
        Restore a soft-deleted object by setting `deleted_at` to NULL.

        :param filter_by: Field-based filters to locate the object.
        :return: Restored domain entity.
        :raises ObjectNotFoundRepoException: If object does not exist or is not deleted.
        """

        stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .where(self.model.deleted_at.is_not(None))
            .values(deleted_at=None)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise ObjectNotFoundRepoException
        return self.mapper.map_to_domain_entity(model)

    async def restore_bulk(self, list_ids: list[Any]) -> int:
        """
        Restore multiple soft-deleted objects by setting `deleted_at=NULL`.

        :param list_ids: List of IDs to restore.
        :return: Number of restored rows.
        """

        stmt = (
            update(self.model)
            .where(self.model.id.in_(list_ids))
            .where(self.model.deleted_at.is_not(None))
            .values(deleted_at=None)
        )
        result = await self.session.execute(stmt)
        return result.rowcount or 0

    async def count(self, filters: dict | None = None) -> int:
        """
        Count active (non-deleted) records in the table with optional filters.

        :param filters: Optional dictionary of field-value filters.
        :return: Number of matching records.
        """

        stmt = select(func.count()).select_from(self.model)
        stmt = self._active_filter(stmt)

        if filters:
            for field, value in filters.items():
                stmt = stmt.where(getattr(self.model, field) == value)

        result = await self.session.execute(stmt)
        return result.scalar_one()
