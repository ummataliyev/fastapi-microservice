from uuid import UUID

from fastapi import APIRouter, status
from fastapi_pagination import Page

from src.api.dependencies.db import DbTransactionDep
from src.schemas.items import ItemCreateSchema, ItemReadSchema, ItemUpdateSchema
from src.services.items import ItemsService

items_router = APIRouter(prefix="/items", tags=["Items"])

_NOT_FOUND = {404: {"description": "Item with the given id does not exist."}}


@items_router.get(
    "",
    response_model=Page[ItemReadSchema],
    summary="List items (paginated)",
    description="Paginated list of active items, ordered by creation time descending.",
    response_description="Page of items + pagination metadata.",
)
async def list_items(db: DbTransactionDep) -> Page[ItemReadSchema]:
    return await ItemsService(db).list()


@items_router.get(
    "/{item_id}",
    response_model=ItemReadSchema,
    summary="Get an item by id",
    description="Returns a single item. Soft-deleted items return 404.",
    responses=_NOT_FOUND,
)
async def get_item(item_id: UUID, db: DbTransactionDep) -> ItemReadSchema:
    return await ItemsService(db).get(item_id)


@items_router.post(
    "",
    response_model=ItemReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create an item",
    description="Creates a new item record.",
    response_description="The created item.",
    responses={422: {"description": "Validation error."}},
)
async def create_item(data: ItemCreateSchema, db: DbTransactionDep) -> ItemReadSchema:
    return await ItemsService(db).create(data)


@items_router.patch(
    "/{item_id}",
    response_model=ItemReadSchema,
    summary="Update an item (partial)",
    description="Updates only the fields you send. Omitted fields are unchanged.",
    responses={**_NOT_FOUND, 422: {"description": "Validation error."}},
)
async def update_item(
    item_id: UUID, data: ItemUpdateSchema, db: DbTransactionDep
) -> ItemReadSchema:
    return await ItemsService(db).update(item_id, data)


@items_router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete an item",
    description="Marks the item as deleted (sets `deleted_at`). Row is preserved.",
    responses=_NOT_FOUND,
)
async def delete_item(item_id: UUID, db: DbTransactionDep) -> None:
    await ItemsService(db).delete(item_id)
