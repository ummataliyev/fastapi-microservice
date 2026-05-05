from src.mappers.base import BaseDataMapper
from src.models.items import Items
from src.schemas.items import ItemReadSchema


class ItemsMapper(BaseDataMapper[Items, ItemReadSchema]):
    model = Items
    schema = ItemReadSchema
