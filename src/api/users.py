from typing import Any
from fastapi import status, APIRouter
from src.services.users import UsersService
from src.api.dependencies import PaginationDep, DbTransactionDep
from src.schemas.users import UserReadSchema, UserCreateSchema, UserUpdateSchema
from src.schemas.pagination import PaginatedResponseSchema
from src.exceptions.service.users import UserNotFound, UserAlreadyExists
from src.exceptions.api.users import (
    UserNotFoundHTTPException,
    UserAlreadyExistsHTTPException,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "",
    response_model=PaginatedResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Get Users List",
    description="Retrieve a paginated list of users with optional email search.",
)
async def list_users(
    db: DbTransactionDep,
    pagination: PaginationDep,
) -> PaginatedResponseSchema:
    return await UsersService(db).get_list(
        limit=pagination.limit,
        offset=pagination.offset,
        current_page=pagination.current_page,
    )


@router.get(
    "/{user_id}",
    response_model=UserReadSchema,
    status_code=status.HTTP_200_OK,
)
async def get_user(user_id: int, db: DbTransactionDep) -> UserReadSchema:
    try:
        return await UsersService(db).get_one_by_id(user_id)
    except UserNotFound as ex:
        raise UserNotFoundHTTPException from ex


@router.post(
    "",
    response_model=UserReadSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(db: DbTransactionDep, data: UserCreateSchema) -> UserReadSchema:
    try:
        return await UsersService(db).create(data)
    except UserAlreadyExists as ex:
        raise UserAlreadyExistsHTTPException from ex


@router.patch(
    "/{user_id}",
    response_model=UserReadSchema,
    status_code=status.HTTP_200_OK,
)
async def update_user(
    user_id: int, db: DbTransactionDep, data: UserUpdateSchema
) -> UserReadSchema:
    try:
        return await UsersService(db).update(user_id, data)
    except UserNotFound as ex:
        raise UserNotFoundHTTPException from ex


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_user(user_id: int, db: DbTransactionDep) -> dict[str, Any]:
    try:
        deleted_id = await UsersService(db).delete(user_id)
        return {"status": "success", "id": deleted_id}
    except UserNotFound as ex:
        raise UserNotFoundHTTPException from ex
