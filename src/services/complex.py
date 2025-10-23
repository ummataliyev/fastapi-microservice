"""
Services for Complex API endpoints.
"""

import uuid

from src.services.base import BaseService

from src.enums.lang import Lang
from src.enums.status import Status
from src.enums.sorting import SortBy

from src.schemas.complex import ComplexReadSchema
from src.schemas.complex import ComplexCreateSchema
from src.schemas.complex import ComplexUpdateSchema
from src.schemas.pagination import PaginatedResponseSchema
from src.schemas.complex import ComplexReadWithCountsSchema
from src.schemas.complex import ComplexReadWithRelationsSchema

from src.exceptions.service.complex import ComplexNotFound
from src.exceptions.service.complex import ComplexAlreadyExists
from src.exceptions.repository.complex import ComplexNotFoundRepoException
from src.exceptions.repository.complex import ComplexAlreadyExistsRepoException


class ComplexService(BaseService):
    """
    Service class to manage Complex objects.
    Provides CRUD operations, pagination, and soft-deletion support.
    """

    async def get_one_by_id(
        self,
        rc_id: uuid.UUID,
    ) -> ComplexReadWithRelationsSchema:
        """
        Retrieve a single residential complex by its UUID.

        :param rc_id: UUID of the residential complex.
        :return: ComplexReadWithRelationsSchema instance representing the residential complex.
        :raises ComplexNotFound: If the residential complex does not exist.
        """

        try:
            complex_data = await self.db.complex.get_one(rc_id=rc_id, with_rels=True)
            return ComplexReadWithRelationsSchema(**complex_data)
        except ComplexNotFoundRepoException as ex:
            raise ComplexNotFound.from_repo(ex)

    async def get_list(
        self,
        limit: int = 10,
        offset: int = 0,
        current_page: int = 1,
        search: str | None = None,
        statuses: list[Status] | None = None,
        sort_by: SortBy | None = None,
        lang: str = Lang.EN,
    ) -> PaginatedResponseSchema[ComplexReadWithCountsSchema]:
        statuses_values = [s.value for s in statuses] if statuses else None

        items, total_items = await self.db.complex.get_all(
            limit=limit,
            offset=offset,
            search=search,
            statuses=statuses_values,
            sort_by=sort_by.value if sort_by else None,
            lang=lang,
        )

        schema_items = [ComplexReadWithCountsSchema(**i) for i in items]

        return self.build_paginated_response(
            items=schema_items,
            total_items=total_items,
            current_page=current_page,
            per_page=limit,
            message="Residential complexes retrieved successfully",
        )

    async def create(self, data: ComplexCreateSchema) -> ComplexReadSchema:
        """
        Create a new residential complex.

        :param data: ComplexCreateSchema instance with creation data.
        :return: Newly created ComplexReadSchema instance.
        :raises ComplexAlreadyExists: If a complex with the same unique fields exists.
        """

        try:
            existing = await self.db.complex.get_one_or_none(name=data.name)
            if existing:
                raise ComplexAlreadyExists(
                    "Residential complex with this name already exists"
                )

        except ComplexAlreadyExistsRepoException as ex:
            raise ComplexAlreadyExists.from_repo(ex)

        try:
            rc = await self.db.complex.add(data)
            await self.db.commit()
            return rc
        except ComplexAlreadyExistsRepoException as ex:
            raise ComplexAlreadyExists.from_repo(ex)

    async def update(
        self, complex_id: uuid.UUID, data: ComplexUpdateSchema
    ) -> ComplexReadSchema:
        """
        Update an existing residential complex.

        :param complex_id: UUID of the complex to update.
        :param data: ComplexUpdateSchema instance with fields to update.
        :return: Updated ComplexReadSchema instance.
        :raises ComplexNotFound: If the residential complex does not exist.
        """

        try:
            updated_rc = await self.db.complex.update_one(
                id=complex_id, data=data, partially=True
            )
            await self.db.commit()
            return updated_rc
        except ComplexNotFoundRepoException as ex:
            raise ComplexNotFound.from_repo(ex)

    async def delete(self, rc_id: uuid.UUID) -> uuid.UUID:
        """
        Delete a residential complex by UUID.

        :param rc_id: UUID of the complex to delete.
        :return: UUID of the deleted residential complex.
        :raises ComplexNotFound: If the residential complex does not exist.
        """

        try:
            deleted = await self.db.complex.delete_one(id=rc_id)
            await self.db.commit()
            return deleted.id
        except ComplexNotFoundRepoException as ex:
            raise ComplexNotFound.from_repo(ex)

    async def restore(self, rc_id: uuid.UUID) -> ComplexReadSchema:
        """
        Restore a soft-deleted residential complex by UUID.

        :param rc_id: UUID of the residential complex to restore.
        :return: Restored ComplexReadSchema instance.
        :raises ComplexNotFound: If the residential complex does not exist.
        """

        try:
            restored_rc = await self.db.complex.restore_one(id=rc_id)
            await self.db.commit()
            return restored_rc
        except ComplexNotFoundRepoException as ex:
            raise ComplexNotFound.from_repo(ex)

    async def restore_many(self, complex_ids: list[uuid.UUID]) -> int:
        """
        Restore multiple residential complexes by their UUIDs.

        :param complex_ids: List of complex UUIDs to restore.
        :return: Number of restored residential complexes.
        """

        count = await self.db.complex.restore_bulk(complex_ids)
        await self.db.commit()
        return count

    async def delete_many(self, complex_ids: list[uuid.UUID]) -> int:
        """
        Bulk delete residential complexes by their UUIDs.

        :param complex_ids: List of complex UUIDs to delete.
        :return: Number of deleted complexes.
        :raises ComplexNotFound: If no complexes were deleted.
        """
        count = await self.db.complex.delete_bulk(complex_ids)
        await self.db.commit()

        if count == 0:
            raise ComplexNotFound(
                f"No residential complexes found for deletion with IDs: {complex_ids}"
            )

        return count
