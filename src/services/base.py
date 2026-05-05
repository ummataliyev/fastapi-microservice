from typing import Generic, TypeVar

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sql_paginate
from sqlalchemy import Select

from src.managers.db.base import BaseTransactionManager

TM = TypeVar("TM", bound=BaseTransactionManager)


class BaseService(Generic[TM]):
    """
    Inherit per domain, e.g. `class ItemsService(BaseService[TransactionManager])`.

    `self.db` is the manager — use `self.db.<repository>` to access repositories
    that the manager wired in `_wire_repositories`.
    """

    def __init__(self, db: TM) -> None:
        self.db = db

    async def paginated_list(
        self,
        query: Select,
        transformer,
    ) -> Page:
        """
        DB-level pagination using `fastapi_pagination.ext.sqlalchemy`.

        - `query` MUST be a `Select` (not a list);
        - `query` MUST include a deterministic ORDER BY for stable paging.
        - `transformer` maps each ORM row to its domain entity, e.g.
              transformer=lambda items: [ItemsMapper.map_to_domain_entity(m) for m in items]
        """
        return await sql_paginate(self.db.session, query, transformer=transformer)
