"""
FastAPI dependency for retrieving the current authenticated user.
"""

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials

from src.managers.auth import AuthManager

from src.schemas.users import UserReadSchema

from src.api.dependencies.db import DbTransactionDep

from src.exceptions.service.auth import InvalidToken
from src.exceptions.service.users import UserNotFound
from src.exceptions.service.auth import InvalidTokenType
from src.exceptions.api.auth import InvalidTokenHTTPException


security = HTTPBearer()


async def get_current_user(
    db: DbTransactionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> UserReadSchema:
    """
    Retrieve the currently authenticated user from a JWT token.

    :param db: Database transaction dependency for repository access.
    :param credentials: HTTP Bearer credentials containing the JWT token.
    :return: UserReadSchema instance representing the current user.
    :raises InvalidTokenHTTPException: 401 if token is invalid, wrong type, or user not found.
    """
    token = credentials.credentials

    auth_manager = AuthManager(db)
    try:
        user = await auth_manager.get_current_user(token)
        return user
    except (InvalidToken, InvalidTokenType, UserNotFound) as ex:
        raise InvalidTokenHTTPException(
            detail=str(ex),
            error_code="AUTH_INVALID_TOKEN",
            headers={"WWW-Authenticate": "Bearer"},
        ) from ex


CurrentUserDep = Annotated[
    UserReadSchema,
    Depends(get_current_user)
]
