from uuid import UUID

from fastapi_pagination import Page

from src.managers.db.transaction import TransactionManager
from src.mappers.items import ItemsMapper
from src.models.items import Items
from src.schemas.items import ItemCreateSchema, ItemReadSchema, ItemUpdateSchema
from src.services.base import BaseService


class ItemsService(BaseService[TransactionManager]):
    async def list(self) -> Page[ItemReadSchema]:
        stmt = self.db.items.list_select().order_by(Items.created_at.desc())
        return await self.paginated_list(
            stmt,
            transformer=lambda rows: [ItemsMapper.map_to_domain_entity(r) for r in rows],
        )

    async def get(self, item_id: UUID) -> ItemReadSchema:
        return await self.db.items.get_one(item_id)

    async def create(self, data: ItemCreateSchema) -> ItemReadSchema:
        return await self.db.items.create(data)

    async def update(self, item_id: UUID, data: ItemUpdateSchema) -> ItemReadSchema:
        payload = data.model_dump(exclude_unset=True)
        return await self.db.items.update(item_id, payload)

    async def delete(self, item_id: UUID) -> None:
        await self.db.items.soft_delete(item_id)
