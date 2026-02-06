"""
Authentication API endpoints.
"""

from fastapi import Request
from fastapi import APIRouter

from src.services.auth import AuthService

from src.core.throttle.limiter import limiter

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
from src.exceptions.service.auth import LoginTemporarilyLocked

from src.exceptions.api.auth import InvalidTokenHTTPException
from src.exceptions.api.auth import AuthUserNotFoundHTTPException
from src.exceptions.api.auth import InvalidCredentialsHTTPException
from src.exceptions.api.users import UserAlreadyExistsHTTPException
from src.exceptions.api.auth import LoginTemporarilyLockedHTTPException


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=TokenResponseSchema,
    status_code=201,
    summary="Register a new user",
    description=("Creates a new user account and returns access and refresh tokens") # noqa
)
@limiter.ppd_limiter()
async def register(
    db: DbTransactionDep,
    data: UserCreateSchema,
    request: Request,
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
        raise UserAlreadyExistsHTTPException(
            detail=str(ex),
            details=getattr(ex, "details", None),
        ) from ex


@router.post(
    "/login",
    response_model=TokenResponseSchema,
    summary="Authenticate user and receive tokens",
    description="Authenticate user and return access/refresh tokens."
)
@limiter.ppd_limiter()
async def login(
    db: DbTransactionDep,
    credentials: LoginSchema,
    request: Request,
):
    """
    Authenticate user and receive access and refresh tokens.

    :param db: Database transaction dependency.
    :param credentials: User credentials containing email and password.
    :return: Access and refresh tokens for the authenticated user.
    """
    try:
        client_ip = request.client.host if request.client else "unknown"
        tokens = await AuthService(db).login(credentials, client_ip=client_ip)
        return tokens
    except InvalidCredentials as ex:
        raise InvalidCredentialsHTTPException(
            detail=str(ex),
            details=getattr(ex, "details", None),
        ) from ex
    except LoginTemporarilyLocked as ex:
        raise LoginTemporarilyLockedHTTPException(
            detail=str(ex),
            details={"retry_after_seconds": ex.retry_after_seconds},
            headers={"Retry-After": str(ex.retry_after_seconds)},
        ) from ex


@router.post(
    "/refresh",
    response_model=TokenResponseSchema,
    summary="Refresh access token",
    description=("Generates a new access token using a valid refresh token")
)
@limiter.ppd_limiter()
async def refresh_token(
    db: DbTransactionDep,
    data: RefreshTokenSchema,
    request: Request,
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
        raise InvalidTokenHTTPException(
            detail=str(ex),
            details=getattr(ex, "details", None),
        ) from ex
    except UserNotFound as ex:
        raise AuthUserNotFoundHTTPException(
            detail=str(ex),
            details=getattr(ex, "details", None),
        ) from ex


@router.get(
    "/me",
    response_model=UserReadSchema,
    summary="Get current user information",
    description=("Retrieves information about the currently authenticated user") # noqa
)
@limiter.ppd_limiter()
async def get_current_user_info(
    current_user: CurrentUserDep,
    request: Request,
):
    """
    Get current authenticated user information.

    :param db: Database transaction dependency.
    :param current_user: Currently authenticated user.
    :return: Information about the authenticated user.
    """
    return current_user
