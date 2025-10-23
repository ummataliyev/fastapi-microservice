"""
Routes for Complex API endpoints.
"""

from uuid import UUID

from typing import Any
from typing import List

from fastapi import Body
from fastapi import Query
from fastapi import status
from fastapi import APIRouter

from src.enums.lang import Lang
from src.enums.status import Status
from src.enums.sorting import SortBy

from src.services.complex import ComplexService

from src.api.dependencies import PaginationDep
from src.api.dependencies import DbTransactionDep

from src.schemas.complex import ComplexReadSchema
from src.schemas.complex import ComplexCreateSchema
from src.schemas.complex import ComplexUpdateSchema
from src.schemas.pagination import PaginatedResponseSchema
from src.schemas.complex import ComplexReadWithCountsSchema
from src.schemas.schemas import BaseHTTPExceptionSchema
from src.schemas.complex import ComplexReadWithRelationsSchema
from src.schemas.complex import ComplexBulkDeleteResponseSchema
from src.schemas.complex import ComplexBulkRestoreResponseSchema

from src.exceptions.service.complex import ComplexNotFound
from src.exceptions.service.complex import ComplexAlreadyExists
from src.exceptions.api.complex import ComplexNotFoundHTTPException
from src.exceptions.api.complex import ComplexAlreadyExistsHTTPException


router = APIRouter(
    prefix="/complexes",
    tags=["Complexes"],
)


@router.get(
    "",
    response_model=PaginatedResponseSchema[ComplexReadWithCountsSchema],
    status_code=status.HTTP_200_OK,
    summary="Get Residential Complexes list",
    description="Retrieve a paginated list of all residential complexes.",
)
async def list_complexes(
    db: DbTransactionDep,
    pagination: PaginationDep,
    search: str | None = Query(None, description="Search by complex name or address"),
    status: Status | None = Query(None, description="Filter by status"),
    sort_by: SortBy | None = Query(None, description="Sorting mode"),
    lang: Lang | None = Query(None, description="Language for content localization"),
) -> PaginatedResponseSchema[ComplexReadWithCountsSchema]:
    """
    Retrieve a paginated list of residential complexes.

    Supports search by name/address, status filtering, and multiple sorting options.
    """
    statuses = [status] if status else None
    lang_value = lang.value if lang else Lang.EN

    return await ComplexService(db).get_list(
        limit=pagination.limit,
        offset=pagination.offset,
        current_page=pagination.current_page,
        search=search,
        statuses=statuses,
        sort_by=sort_by,
        lang=lang_value,
    )


@router.post(
    "",
    response_model=ComplexReadSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        ComplexAlreadyExistsHTTPException.status_code: {
            "model": BaseHTTPExceptionSchema,
            "description": ComplexAlreadyExistsHTTPException.message,
        },
    },
    summary="Create Residential Complex",
    description="Create a new residential complex with the provided details.",
)
async def create_complex(
    db: DbTransactionDep,
    data: ComplexCreateSchema,
) -> ComplexReadSchema:
    """
    Create a new residential complex.

    :param db: The database transaction dependency.
    :param data: The schema containing the residential complex details.
    :raises ComplexAlreadyExistsHTTPException: If a complex with the same name already exists.
    :return: The created residential complex schema object.
    """
    try:
        return await ComplexService(db).create(data)
    except ComplexAlreadyExists as ex:
        raise ComplexAlreadyExistsHTTPException from ex


@router.patch(
    "/restore-bulk",
    response_model=ComplexBulkRestoreResponseSchema,
    status_code=status.HTTP_200_OK,
    responses={
        ComplexNotFoundHTTPException.status_code: {
            "model": BaseHTTPExceptionSchema,
            "description": ComplexNotFoundHTTPException.message,
        },
    },
    summary="Bulk Restore Residential Complexes",
    description="Restore multiple previously deleted residential complexes by their IDs.",
)
async def restore_complexes(
    db: DbTransactionDep,
    complex_ids: List[UUID] = Body(..., embed=True),
) -> ComplexBulkRestoreResponseSchema:
    """
    Restore multiple previously deleted residential complexes.

    :param db: Database transaction dependency.
    :param complex_ids: List of UUIDs for complexes to restore.
    :raises ComplexNotFoundHTTPException: If any complex is not found.
    :return: Schema with status and number of restored complexes.
    """
    try:
        count = await ComplexService(db).restore_many(complex_ids=complex_ids)
        return ComplexBulkRestoreResponseSchema(status="success", restored=count)
    except ComplexNotFound as ex:
        raise ComplexNotFoundHTTPException from ex


@router.patch(
    "/{complex_id}",
    response_model=ComplexReadSchema,
    status_code=status.HTTP_200_OK,
    responses={
        ComplexNotFoundHTTPException.status_code: {
            "model": BaseHTTPExceptionSchema,
            "description": ComplexNotFoundHTTPException.message,
        },
    },
    summary="Update Residential Complex",
    description="Update an existing residential complex by its ID.",
)
async def update_complex(
    complex_id: UUID,
    db: DbTransactionDep,
    data: ComplexUpdateSchema,
) -> ComplexReadSchema:
    """
    Update an existing residential complex.

    :param complex_id: The UUID of the residential complex to update.
    :param db: The database transaction dependency.
    :param data: The schema containing updated data.
    :raises ComplexNotFoundHTTPException: If the complex is not found.
    :return: The updated residential complex schema object.
    """
    try:
        return await ComplexService(db).update(complex_id, data)
    except ComplexNotFound as ex:
        raise ComplexNotFoundHTTPException from ex


@router.delete(
    "/{complex_id}",
    status_code=status.HTTP_200_OK,
    responses={
        ComplexNotFoundHTTPException.status_code: {
            "model": BaseHTTPExceptionSchema,
            "description": ComplexNotFoundHTTPException.message,
        },
    },
    summary="Delete Residential Complex",
    description="Delete a residential complex by its ID.",
)
async def delete_complex(
    complex_id: UUID,
    db: DbTransactionDep,
) -> dict[str, Any]:
    """
    Delete a residential complex by its UUID.

    :param complex_id: The UUID of the residential complex to delete.
    :param db: The database transaction dependency.
    :raises ComplexNotFoundHTTPException: If the complex is not found.
    :return: Success message and deleted ID.
    """
    try:
        deleted_id = await ComplexService(db).delete(complex_id)
        return {"status": "success", "id": deleted_id}
    except ComplexNotFound as ex:
        raise ComplexNotFoundHTTPException from ex


@router.patch(
    "/{complex_id}/restore",
    response_model=ComplexReadSchema,
    status_code=status.HTTP_200_OK,
    responses={
        ComplexNotFoundHTTPException.status_code: {
            "model": BaseHTTPExceptionSchema,
            "description": ComplexNotFoundHTTPException.message,
        },
    },
    summary="Restore Residential Complex",
    description="Restore a previously deleted residential complex by its ID.",
)
async def restore_complex(
    complex_id: UUID,
    db: DbTransactionDep,
) -> ComplexReadSchema:
    """
    Restore a previously deleted residential complex.

    :param complex_id: The UUID of the complex to restore.
    :param db: The database transaction dependency.
    :raises ComplexNotFoundHTTPException: If the complex is not found.
    :return: The restored complex schema object.
    """
    try:
        return await ComplexService(db).restore(complex_id)
    except ComplexNotFound as ex:
        raise ComplexNotFoundHTTPException from ex


@router.get(
    "/{complex_id}",
    response_model=ComplexReadWithRelationsSchema,
    status_code=status.HTTP_200_OK,
    responses={
        ComplexNotFoundHTTPException.status_code: {
            "model": BaseHTTPExceptionSchema,
            "description": ComplexNotFoundHTTPException.message,
        },
    },
    summary="Get Residential Complex by ID",
    description="Fetch a single residential complex by its unique ID.",
)
async def get_complex(
    complex_id: UUID,
    db: DbTransactionDep,
) -> ComplexReadWithRelationsSchema:
    """
    Retrieve a single residential complex by its unique identifier.

    :param complex_id: The UUID of the residential complex.
    :param db: The database transaction dependency.
    :raises ComplexNotFoundHTTPException: If the complex is not found.
    :return: The residential complex schema object.
    """
    try:
        return await ComplexService(db).get_one_by_id(rc_id=complex_id)
    except ComplexNotFound as ex:
        raise ComplexNotFoundHTTPException from ex


@router.post(
    "/bulk-delete",
    response_model=ComplexBulkDeleteResponseSchema,
    status_code=status.HTTP_200_OK,
    responses={
        ComplexNotFoundHTTPException.status_code: {
            "model": BaseHTTPExceptionSchema,
            "description": ComplexNotFoundHTTPException.message,
        },
    },
    summary="Bulk Delete Residential Complexes",
    description="Soft delete multiple residential complexes by their IDs.",
)
async def delete_complexes(
    db: DbTransactionDep,
    complex_ids: List[UUID] = Body(..., embed=True),
) -> ComplexBulkDeleteResponseSchema:
    """
    Delete multiple residential complexes by UUIDs.

    :param db: Database transaction dependency.
    :param complex_ids: List of complex UUIDs to delete.
    :raises ComplexNotFoundHTTPException: If no complexes were deleted.
    :return: Schema with status and number of deleted complexes.
    """
    try:
        deleted_count = await ComplexService(db).delete_many(complex_ids)
        return ComplexBulkDeleteResponseSchema(status="success", deleted=deleted_count)
    except ComplexNotFound as ex:
        raise ComplexNotFoundHTTPException from ex
