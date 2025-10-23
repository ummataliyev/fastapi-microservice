"""
Pagination dependencies for FastAPI routes.
"""

from typing import Annotated

from fastapi import Depends

from src.schemas.pagination import PaginationSchema
from src.schemas.pagination import PaginationRequestSchema


def get_pagination_params(
    params: Annotated[
        PaginationRequestSchema,
        Depends(),
    ],
) -> PaginationSchema:
    """
    Convert raw pagination query parameters into a structured `PaginationSchema`.

    :param params: PaginationRequestSchema containing:
        - page (int): Current page number (1-indexed).
        - per_page (int): Number of items per page.
    :type params: PaginationRequestSchema
    :return: PaginationSchema containing calculated limit, offset, and current_page.
    :rtype: PaginationSchema
    """

    return PaginationSchema(
        limit=params.per_page,
        offset=params.per_page * (params.page - 1),
        current_page=params.page,
    )


PaginationDep = Annotated[
    PaginationSchema,
    Depends(get_pagination_params),
]
