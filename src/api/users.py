"""
User management API endpoints.
"""

from typing import Any

from fastapi import status
from fastapi import APIRouter

from src.services.users import UsersService

from src.api.dependencies import PaginationDep
from src.api.dependencies import CurrentUserDep
from src.api.dependencies import DbTransactionDep

from src.schemas.users import UserReadSchema
from src.schemas.users import UserCreateSchema
from src.schemas.users import UserUpdateSchema
from src.schemas.pagination import PaginatedResponseSchema

from src.exceptions.service.users import UserNotFound
from src.exceptions.service.users import UserAlreadyExists
from src.exceptions.api.users import UserNotFoundHTTPException
from src.exceptions.api.users import UserAlreadyExistsHTTPException


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "",
    response_model=PaginatedResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="List users",
    description="Retrieve a paginated list of all users with optional email filtering",
)
async def list(
    db: DbTransactionDep,
    pagination: PaginationDep,
    current_user: CurrentUserDep
) -> PaginatedResponseSchema:
    """
    Get a paginated list of users.

    :param db: Database transaction dependency.
    :param pagination: Pagination parameters (limit, offset, current_page).
    :return: Paginated list of user records.
    """
    return await UsersService(db).get_list(
        limit=pagination.limit,
        offset=pagination.offset,
        current_page=pagination.current_page,
    )


@router.get(
    "/{user_id}",
    response_model=UserReadSchema,
    status_code=status.HTTP_200_OK,
    summary="Get user by ID",
    description="Retrieve detailed information for a specific user by ID",
)
async def get(
    user_id: int,
    db: DbTransactionDep,
    current_user: CurrentUserDep
) -> UserReadSchema:
    """
    Get user details by ID.

    :param user_id: User ID to retrieve.
    :param db: Database transaction dependency.
    :return: User details.
    """
    try:
        return await UsersService(db).get_one_by_id(user_id)
    except UserNotFound as ex:
        raise UserNotFoundHTTPException from ex


@router.post(
    "",
    response_model=UserReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user",
    description="Create a new user record in the database",
)
async def create(
    db: DbTransactionDep,
    data: UserCreateSchema,
    current_user: CurrentUserDep,
) -> UserReadSchema:
    """
    Create a new user.

    :param db: Database transaction dependency.
    :param data: User creation payload.
    :return: Created user record.
    :raises UserAlreadyExistsHTTPException: If a user with the same email exists.
    """
    try:
        return await UsersService(db).create(data)
    except UserAlreadyExists as ex:
        raise UserAlreadyExistsHTTPException from ex


@router.patch(
    "/{user_id}",
    response_model=UserReadSchema,
    status_code=status.HTTP_200_OK,
    summary="Update user",
    description="Update user information partially by user ID.",
)
async def update(
    user_id: int,
    db: DbTransactionDep,
    data: UserUpdateSchema,
    current_user: CurrentUserDep,
) -> UserReadSchema:
    """
    Update user information by ID.

    :param user_id: ID of the user to update.
    :param db: Database transaction dependency.
    :param data: Updated user data.
    :return: Updated user record.
    """
    try:
        return await UsersService(db).update(user_id, data)
    except UserNotFound as ex:
        raise UserNotFoundHTTPException from ex


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete user",
    description="Delete a user from the database by ID.",
)
async def delete(
    user_id: int,
    db: DbTransactionDep,
    current_user: CurrentUserDep,
) -> dict[str, Any]:
    """
    Delete a user by ID.

    :param user_id: ID of the user to delete.
    :param db: Database transaction dependency.
    :return: Deletion status with user ID.
    """
    try:
        deleted_id = await UsersService(db).delete(user_id)
        return {"status": "success", "id": deleted_id}
    except UserNotFound as ex:
        raise UserNotFoundHTTPException from ex
