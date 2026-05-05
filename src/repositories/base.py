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
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.sqlalchemy import Base

from src.mappers.base import BaseDataMapper

from src.exceptions.repository.base import ObjectNotFoundRepoException
from src.exceptions.repository.base import CannotAddObjectRepoException
from src.exceptions.repository.base import CannotUpdateObjectRepoException
from src.exceptions.repository.base import CannotDeleteObjectRepoException
from src.exceptions.repository.base import InvalidRepositoryInputRepoException


T = TypeVar("T")


class BaseRepository(Generic[T]):
    """
    Base repository providing generic CRUD operations for SQLAlchemy models.
    """

    model: type[Base] | None = None
    mapper: type[BaseDataMapper] | None = None

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

    def _validate_filter_fields(self, filters: dict[str, Any]) -> None:
        """
        Validate that all filter keys are valid model attributes.
        """

        for field in filters:
            if not hasattr(self.model, field):
                raise InvalidRepositoryInputRepoException(
                    f"Unknown filter field: {field}"
                )

    def _ensure_soft_delete_supported(self) -> None:
        """
        Ensure current model supports soft deletion operations.
        """

        if not hasattr(self.model, "deleted_at"):
            raise InvalidRepositoryInputRepoException(
                f"Model {self.model.__name__} does not support soft deletion"
            )

    def _supports_returning(self) -> bool:
        """
        Determine whether the current DB dialect supports DML RETURNING in this project setup.

        :return: True when safe to use RETURNING clauses, otherwise False.
        :rtype: bool
        :raises Exception: If dialect inspection fails unexpectedly.
        """
        bind = self.session.get_bind()
        dialect_name = bind.dialect.name if bind is not None else ""
        return dialect_name not in {"mysql", "mariadb"}

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

        self._validate_filter_fields(filter_by)
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
        except MultipleResultsFound as ex:
            raise InvalidRepositoryInputRepoException(
                "Multiple objects matched filters expected to return one"
            ) from ex

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
            raise InvalidRepositoryInputRepoException("Limit and offset must be non-negative.")
        self._validate_filter_fields(filter_by)

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

        self._validate_filter_fields(filter_by)
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

        payload = data.model_dump()
        try:
            if self._supports_returning():
                stmt = insert(self.model).values(**payload).returning(self.model)
                result = await self.session.execute(stmt)
                model = result.scalar_one()
            else:
                model = self.model(**payload)
                self.session.add(model)
                await self.session.flush()
                await self.session.refresh(model)
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

        self._validate_filter_fields(filter_by)
        update_payload = data.model_dump(exclude_unset=partially)
        if not update_payload:
            raise InvalidRepositoryInputRepoException("No fields provided for update.")

        try:
            if self._supports_returning():
                stmt = (
                    update(self.model)
                    .values(**update_payload)
                    .filter_by(**filter_by)
                    .returning(self.model)
                )
                result = await self.session.execute(stmt)
                model = result.scalar_one()
            else:
                stmt = update(self.model).values(**update_payload).filter_by(**filter_by)
                result = await self.session.execute(stmt)
                if (result.rowcount or 0) == 0:
                    raise ObjectNotFoundRepoException
                select_stmt = select(self.model).filter_by(**filter_by)
                selected = await self.session.execute(select_stmt)
                model = selected.scalar_one()
        except NoResultFound as ex:
            raise ObjectNotFoundRepoException from ex
        except IntegrityError as ex:
            raise CannotUpdateObjectRepoException from ex
        return self.mapper.map_to_domain_entity(model)

    async def delete_one(self, **filter_by) -> T:
        """
        Soft-delete a single object by setting `deleted_at` timestamp.

        :param filter_by: Field-based filters to locate the object.
        :return: Deleted domain entity.
        :raises ObjectNotFoundRepoException: If object does not exist.
        """

        self._ensure_soft_delete_supported()
        self._validate_filter_fields(filter_by)
        try:
            if self._supports_returning():
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
            else:
                stmt = (
                    update(self.model)
                    .filter_by(**filter_by)
                    .where(self.model.deleted_at.is_(None))
                    .values(deleted_at=func.now())
                )
                result = await self.session.execute(stmt)
                if (result.rowcount or 0) == 0:
                    raise ObjectNotFoundRepoException
                select_stmt = (
                    select(self.model)
                    .filter_by(**filter_by)
                    .where(self.model.deleted_at.is_not(None))
                )
                selected = await self.session.execute(select_stmt)
                model = selected.scalar_one()
        except IntegrityError as ex:
            raise CannotDeleteObjectRepoException from ex
        return self.mapper.map_to_domain_entity(model)

    async def delete_bulk(self, list_ids: list[Any]) -> int:
        """
        Soft-delete multiple objects by setting `deleted_at`.

        :param list_ids: List of IDs to delete.
        :return: Number of deleted rows.
        """

        self._ensure_soft_delete_supported()
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

        self._ensure_soft_delete_supported()
        self._validate_filter_fields(filter_by)
        try:
            if self._supports_returning():
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
            else:
                stmt = (
                    update(self.model)
                    .filter_by(**filter_by)
                    .where(self.model.deleted_at.is_not(None))
                    .values(deleted_at=None)
                )
                result = await self.session.execute(stmt)
                if (result.rowcount or 0) == 0:
                    raise ObjectNotFoundRepoException
                select_stmt = (
                    select(self.model)
                    .filter_by(**filter_by)
                    .where(self.model.deleted_at.is_(None))
                )
                selected = await self.session.execute(select_stmt)
                model = selected.scalar_one()
        except IntegrityError as ex:
            raise CannotUpdateObjectRepoException from ex
        return self.mapper.map_to_domain_entity(model)

    async def restore_bulk(self, list_ids: list[Any]) -> int:
        """
        Restore multiple soft-deleted objects by setting `deleted_at=NULL`.

        :param list_ids: List of IDs to restore.
        :return: Number of restored rows.
        """

        self._ensure_soft_delete_supported()
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
            self._validate_filter_fields(filters)
            for field, value in filters.items():
                stmt = stmt.where(getattr(self.model, field) == value)

        result = await self.session.execute(stmt)
        return result.scalar_one()
