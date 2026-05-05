from uuid import UUID

from fastapi import APIRouter, status
from fastapi_pagination import Page

from src.api.dependencies.auth import CurrentUserDep
from src.api.dependencies.db import DbTransactionDep
from src.schemas.users import (
    UserCreateSchema,
    UserReadSchema,
    UserUpdateSchema,
)
from src.services.users import UsersService

users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.get("", response_model=Page[UserReadSchema])
async def list_users(db: DbTransactionDep, _: CurrentUserDep) -> Page[UserReadSchema]:
    return await UsersService(db).list()


@users_router.get("/{user_id}", response_model=UserReadSchema)
async def get_user(user_id: UUID, db: DbTransactionDep, _: CurrentUserDep) -> UserReadSchema:
    return await UsersService(db).get(user_id)


@users_router.post("", response_model=UserReadSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreateSchema, db: DbTransactionDep, _: CurrentUserDep
) -> UserReadSchema:
    return await UsersService(db).create(data)


@users_router.patch("/{user_id}", response_model=UserReadSchema)
async def update_user(
    user_id: UUID,
    data: UserUpdateSchema,
    db: DbTransactionDep,
    _: CurrentUserDep,
) -> UserReadSchema:
    return await UsersService(db).update(user_id, data)


@users_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID, db: DbTransactionDep, _: CurrentUserDep
) -> None:
    await UsersService(db).delete(user_id)
