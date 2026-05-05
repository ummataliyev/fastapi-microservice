from sqlalchemy import select

from src.mappers.items import ItemsMapper
from src.models.items import Items
from src.repositories.base import BaseRepository
from src.schemas.items import ItemReadSchema


class ItemsRepository(BaseRepository[Items, ItemReadSchema]):
    model = Items
    mapper = ItemsMapper
    entity_name = "Item"

    def list_select(self):
        """Public Select for pagination — applies the soft-delete filter."""
        return self._active_filter(select(Items))
