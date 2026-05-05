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

users_router = APIRouter(prefix="/users", tags=["Users"])

_UNAUTHORIZED = {401: {"description": "Missing or invalid access token."}}
_NOT_FOUND = {404: {"description": "User with the given id does not exist."}}


@users_router.get(
    "",
    response_model=Page[UserReadSchema],
    summary="List users (paginated)",
    description=(
        "Returns a paginated list of active (non-soft-deleted) users, ordered "
        "by `created_at` descending. Use `page` and `size` query parameters "
        "to navigate."
    ),
    response_description="A page of users plus pagination metadata.",
    responses=_UNAUTHORIZED,
)
async def list_users(db: DbTransactionDep, _: CurrentUserDep) -> Page[UserReadSchema]:
    return await UsersService(db).list()


@users_router.get(
    "/{user_id}",
    response_model=UserReadSchema,
    summary="Get a user by id",
    description="Returns a single user by UUID. Soft-deleted users return 404.",
    response_description="The user record.",
    responses={**_UNAUTHORIZED, **_NOT_FOUND},
)
async def get_user(user_id: UUID, db: DbTransactionDep, _: CurrentUserDep) -> UserReadSchema:
    return await UsersService(db).get(user_id)


@users_router.post(
    "",
    response_model=UserReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user",
    description=(
        "Admin-style user creation. Hashes the password with bcrypt and stores "
        "the email lowercase. Use `/auth/register` for self-service signups."
    ),
    response_description="The created user record.",
    responses={
        **_UNAUTHORIZED,
        409: {"description": "A user with this email already exists."},
        422: {"description": "Validation error (bad email, weak password)."},
    },
)
async def create_user(
    data: UserCreateSchema, db: DbTransactionDep, _: CurrentUserDep
) -> UserReadSchema:
    return await UsersService(db).create(data)


@users_router.patch(
    "/{user_id}",
    response_model=UserReadSchema,
    summary="Update a user (partial)",
    description=(
        "Updates only the fields you send. If `password` is provided, it is "
        "re-hashed before storage. If `email` is provided, it is lowercased."
    ),
    response_description="The updated user record.",
    responses={**_UNAUTHORIZED, **_NOT_FOUND, 422: {"description": "Validation error."}},
)
async def update_user(
    user_id: UUID,
    data: UserUpdateSchema,
    db: DbTransactionDep,
    _: CurrentUserDep,
) -> UserReadSchema:
    return await UsersService(db).update(user_id, data)


@users_router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete a user",
    description=(
        "Marks the user as deleted by setting `deleted_at`. The row is NOT "
        "removed from the database; subsequent reads filter it out via the "
        "soft-delete clause in `BaseRepository._active_filter`."
    ),
    response_description="No content.",
    responses={**_UNAUTHORIZED, **_NOT_FOUND},
)
async def delete_user(
    user_id: UUID, db: DbTransactionDep, _: CurrentUserDep
) -> None:
    await UsersService(db).delete(user_id)
