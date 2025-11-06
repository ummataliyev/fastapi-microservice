"""
FastAPI dependencies for JWT authentication.
"""

from typing import Annotated

from fastapi import status
from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials

from src.services.auth import AuthService
from src.schemas.users import UserReadSchema
from src.api.dependencies.db import DbTransactionDep
from src.exceptions.service.auth import InvalidToken
from src.exceptions.service.users import UserNotFound
from src.exceptions.service.auth import InvalidTokenType


security = HTTPBearer()


async def get_current_user(
    db: DbTransactionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> UserReadSchema:
    """
    Dependency to get current authenticated user from JWT token.

    :param credentials: HTTP Bearer credentials containing JWT token.
    :param auth_service: Authentication service instance.
    :return: Current user data.
    :raises HTTPException: If authentication fails.
    """
    token = credentials.credentials

    try:
        user = await AuthService(db).get_current_user(token)
        return user
    except (InvalidToken, InvalidTokenType) as ex:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(ex),
            headers={"WWW-Authenticate": "Bearer"},
        )

    except UserNotFound:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )


CurrentUser = Annotated[
    UserReadSchema,
    Depends(get_current_user)
]
