"""
Repository for Complex API endpoints.
"""

import uuid

from typing import List
from typing import Tuple
from typing import TypeVar

from sqlalchemy import or_
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import nullsfirst
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy.exc import MultipleResultsFound

from src.enums.lang import Lang
from src.enums.status import Status
from src.enums.sorting import SortBy

from src.models.floor import Floor
from src.models.section import Section
from src.models.complex import Complex
from src.models.users import Building
from src.models.apartment import Apartment

from src.mappers.complex import ComplexMapper
from src.mappers.building import BuildingMapper

from src.repositories.base import BaseRepository

from src.exceptions.api.base import BaseHTTPException
from src.exceptions.repository.base import BaseRepoException
from src.exceptions.repository.base import ObjectNotFoundRepoException
from src.exceptions.repository.complex import ComplexNotFoundRepoException
from src.exceptions.repository.complex import ComplexAlreadyExistsRepoException


T = TypeVar("T")


class ComplexRepository(BaseRepository):
    """
    Repository for managing Complex persistence and retrieval.
    """

    model = Complex
    mapper = ComplexMapper

    async def get_all(
        self,
        limit: int = 10,
        offset: int = 0,
        with_rels: bool = False,
        search: str | None = None,
        statuses: list[str] | None = None,
        sort_by: str | None = None,
        lang: str = Lang.EN,
    ) -> Tuple[List[T], int]:
        """
        Retrieve a paginated list of residential complexes with optional filters and sorting.

        Args:
            limit: Maximum number of items to return
            offset: Number of items to skip
            with_rels: Whether to include relationships
            search: Search term for name/address
            statuses: List of status values to filter by
            sort_by: Sort order (alphabetical, newest, oldest)
            lang: Language for alphabetical sorting

        Returns:
            Tuple of (items list, total count)

        Raises:
            BaseRepoException: If limit/offset are negative
            ComplexNotFoundRepoException: If requested page doesn't exist
        """
        if limit < 0 or offset < 0:
            raise BaseRepoException("Limit and offset must be non-negative.")

        base_query = (
            select(
                self.model,
                func.count(func.distinct(Building.id)).label("building_count"),
                func.count(func.distinct(Section.id)).label("section_count"),
                func.count(func.distinct(Floor.id)).label("floor_count"),
                func.count(func.distinct(Apartment.id)).label("apartment_count"),
            )
            .outerjoin(Building, Building.complex_id == self.model.id)
            .outerjoin(Section, Section.building_id == Building.id)
            .outerjoin(Floor, Floor.section_id == Section.id)
            .outerjoin(Apartment, Apartment.floor_id == Floor.id)
            .group_by(self.model.id)
        )

        if statuses:
            if Status.DELETED.value in statuses:
                base_query = base_query.where(self.model.deleted_at.isnot(None))
            else:
                base_query = base_query.where(
                    self.model.deleted_at.is_(None),
                    self.model.status.in_(statuses)
                )
        else:
            base_query = base_query.where(self.model.deleted_at.is_(None))

        if search:
            search_pattern = f"%{search}%"
            base_query = base_query.where(
                or_(
                    self.model.name["uz"].astext.ilike(search_pattern),
                    self.model.name["ru"].astext.ilike(search_pattern),
                    self.model.name["en"].astext.ilike(search_pattern),
                    self.model.address["uz"].astext.ilike(search_pattern),
                    self.model.address["ru"].astext.ilike(search_pattern),
                    self.model.address["en"].astext.ilike(search_pattern),
                )
            )

        if sort_by == SortBy.ALPHABETICAL.value:
            lang_field = func.coalesce(
                self.model.name[lang].astext,
                self.model.name["en"].astext,
                self.model.name["ru"].astext,
                self.model.name["uz"].astext,
            )
            base_query = base_query.order_by(nullsfirst(lang_field.asc()))
        elif sort_by == SortBy.NEWEST.value:
            base_query = base_query.order_by(self.model.created_at.desc())
        elif sort_by == SortBy.OLDEST.value:
            base_query = base_query.order_by(self.model.created_at.asc())
        else:
            base_query = base_query.order_by(self.model.id.desc())

        total_items = await self.session.scalar(
            select(func.count()).select_from(base_query.subquery())
        )

        if total_items == 0:
            return [], 0

        if offset >= total_items:
            raise BaseHTTPException(
                status_code=404,
                detail="Requested page does not exist."
            )

        query = base_query.limit(limit).offset(offset)
        result = await self.session.execute(query)

        items = []
        for row in result.all():
            complex_obj, building_count, section_count, floor_count, apartment_count = row
            item = self.mapper.map_to_domain_entity(complex_obj, with_rels=with_rels)
            items.append({
                **item.model_dump(),
                "building_count": building_count,
                "section_count": section_count,
                "floor_count": floor_count,
                "apartment_count": apartment_count,
            })

        return items, total_items

    async def get_one(self, rc_id: uuid.UUID, with_rels: bool = True) -> T:
        """
        Retrieve a residential complex by its UUID along with counts of related entities.
        """
        query = select(self.model).where(self.model.id == rc_id, self.model.deleted_at.is_(None))
        if with_rels:
            query = query.options(
                selectinload(self.model.buildings),
                with_loader_criteria(Building, lambda cls: cls.deleted_at.is_(None), include_aliases=True),
            )

        result = await self.session.execute(query)
        complex_obj = result.scalar_one_or_none()
        if not complex_obj:
            raise ComplexNotFoundRepoException(f"Complex {rc_id} not found")

        base_data = self.mapper.map_to_domain_entity(complex_obj, with_rels=False)
        base_dict = base_data.model_dump()
        base_dict["buildings"] = []

        for b in complex_obj.buildings:
            if b.deleted_at:
                continue

            section_count = await self.session.scalar(
                select(func.count())
                .select_from(Section)
                .where(
                    Section.building_id == b.id,
                    Section.deleted_at.is_(None)
                )
            )

            floor_count = await self.session.scalar(
                select(func.count())
                .select_from(Floor)
                .join(Section, Floor.section_id == Section.id)
                .where(Section.building_id == b.id, Floor.deleted_at.is_(None))
            )

            apartment_count = await self.session.scalar(
                select(func.count())
                .select_from(Apartment)
                .join(Floor, Apartment.floor_id == Floor.id)
                .join(Section, Floor.section_id == Section.id)
                .where(Section.building_id == b.id, Apartment.deleted_at.is_(None))
            )

            base_dict["buildings"].append(
                {
                    **BuildingMapper.map_to_domain_entity(
                        model_instance=b,
                        with_rels=False
                    ).model_dump(),
                    "section_count": section_count,
                    "floor_count": floor_count,
                    "apartment_count": apartment_count,
                }
            )

        return {
            **base_dict,
            "building_count": len(base_dict["buildings"]),
            "section_count": sum(b["section_count"] for b in base_dict["buildings"]),
            "floor_count": sum(b["floor_count"] for b in base_dict["buildings"]),
            "apartment_count": sum(b["apartment_count"] for b in base_dict["buildings"]),
        }

    async def get_one_or_none(self, **filter_by) -> T | None:
        """
        Retrieve a single object matching the filter, or return None.
        """
        if "name" in filter_by:
            count_stmt = select(
                func.count()
            ).select_from(self.model).where(self.model.name == filter_by["name"])
            result = await self.session.execute(count_stmt)
            count = result.scalar_one()
            if count > 1:
                raise ComplexAlreadyExistsRepoException(
                    message="Multiple complexes with the same name exist"
                )

        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)

        try:
            model = result.scalar_one_or_none()
        except MultipleResultsFound as ex:
            raise ComplexAlreadyExistsRepoException from ex

        if not model:
            return None
        return self.mapper.map_to_domain_entity(model)

    async def update_one(self, **kwargs):
        try:
            return await super().update_one(**kwargs)
        except ObjectNotFoundRepoException as ex:
            raise ComplexNotFoundRepoException from ex

    async def delete_one(self, **kwargs):
        try:
            return await super().delete_one(**kwargs)
        except ObjectNotFoundRepoException as ex:
            raise ComplexNotFoundRepoException from ex
