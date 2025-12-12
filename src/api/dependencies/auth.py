"""
FastAPI dependency for retrieving the current authenticated user.
"""

from typing import Annotated

from fastapi import status
from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials

from src.managers.auth import AuthManager

from src.schemas.users import UserReadSchema

from src.api.dependencies.db import DbTransactionDep

from src.exceptions.service.auth import InvalidToken
from src.exceptions.service.auth import InvalidTokenType
from src.exceptions.service.users import UserNotFound


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
    :raises HTTPException: 401 if token is invalid, wrong type, or user not found.
    """
    token = credentials.credentials

    auth_manager = AuthManager(db)
    try:
        user = await auth_manager.get_current_user(token)
        return user
    except (InvalidToken, InvalidTokenType, UserNotFound) as ex:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(ex),
            headers={"WWW-Authenticate": "Bearer"},
        )


CurrentUserDep = Annotated[
    UserReadSchema,
    Depends(get_current_user)
]
