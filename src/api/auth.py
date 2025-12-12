"""
Authentication API endpoints.
"""

from fastapi import status
from fastapi import APIRouter
from fastapi import HTTPException

from src.services.auth import AuthService

from src.schemas.auth import LoginSchema
from src.schemas.users import UserReadSchema
from src.schemas.users import UserCreateSchema
from src.schemas.auth import RefreshTokenSchema
from src.schemas.auth import TokenResponseSchema

from src.api.dependencies import CurrentUserDep
from src.api.dependencies import DbTransactionDep

from src.exceptions.service.auth import InvalidToken
from src.exceptions.service.users import UserNotFound
from src.exceptions.service.auth import InvalidTokenType
from src.exceptions.service.auth import InvalidCredentials
from src.exceptions.service.users import UserAlreadyExists


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=TokenResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description=("Creates a new user account and returns access and refresh tokens") # noqa
)
async def register(
    db: DbTransactionDep,
    data: UserCreateSchema,
):
    """
    Register a new user and receive access and refresh tokens.

    :param db: Database transaction dependency.
    :param data: User registration data including email and password.
    :return: Newly generated access and refresh tokens for the registered user.
    """
    try:
        tokens = await AuthService(db).register(data)
        return tokens
    except UserAlreadyExists as ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ex)
        )


@router.post(
    "/login",
    response_model=TokenResponseSchema,
    summary="Authenticate user and receive tokens",
    description="Authenticate user and return access/refresh tokens."
)
async def login(
    db: DbTransactionDep,
    credentials: LoginSchema,
):
    """
    Authenticate user and receive access and refresh tokens.

    :param db: Database transaction dependency.
    :param credentials: User credentials containing email and password.
    :return: Access and refresh tokens for the authenticated user.
    """
    try:
        tokens = await AuthService(db).login(credentials)
        return tokens
    except InvalidCredentials as ex:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(ex)
        )


@router.post(
    "/refresh",
    response_model=TokenResponseSchema,
    summary="Refresh access token",
    description=("Generates a new access token using a valid refresh token")
)
async def refresh_token(
    db: DbTransactionDep,
    data: RefreshTokenSchema,
):
    """
    Refresh access token using refresh token.

    :param db: Database transaction dependency.
    :param data: Schema containing the refresh token.
    :return: A new access token and the same refresh token.
    """
    try:
        tokens = await AuthService(db).refresh_access_token(data.refresh_token)
        return tokens
    except (InvalidToken, InvalidTokenType) as ex:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(ex)
        )
    except UserNotFound as ex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ex)
        )


@router.get(
    "/me",
    response_model=UserReadSchema,
    summary="Get current user information",
    description=("Retrieves information about the currently authenticated user") # noqa
)
async def get_current_user_info(
    current_user: CurrentUserDep
):
    """
    Get current authenticated user information.

    :param db: Database transaction dependency.
    :param current_user: Currently authenticated user.
    :return: Information about the authenticated user.
    """
    return current_user
