from fastapi import APIRouter, status

from src.api.dependencies.auth import CurrentUserDep
from src.api.dependencies.db import DbTransactionDep
from src.schemas.auth import (
    LoginSchema,
    RefreshTokenSchema,
    TokenResponseSchema,
)
from src.schemas.users import UserCreateSchema
from src.services.auth import AuthService

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post(
    "/register",
    response_model=TokenResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description=(
        "Creates a new user account and immediately returns a fresh access + "
        "refresh token pair. Email is normalised to lowercase before storage."
    ),
    response_description="Token pair for the newly created user.",
    responses={
        409: {"description": "A user with this email already exists."},
        422: {"description": "Validation error (bad email, weak password)."},
    },
)
async def register(data: UserCreateSchema, db: DbTransactionDep) -> TokenResponseSchema:
    return await AuthService(db).register(data)


@auth_router.post(
    "/login",
    response_model=TokenResponseSchema,
    summary="Log in with email and password",
    description=(
        "Verifies the credentials and returns a fresh access + refresh token "
        "pair. Email matching is case-insensitive (stored lowercase)."
    ),
    response_description="Token pair for the authenticated user.",
    responses={
        401: {"description": "Invalid email or password."},
        422: {"description": "Validation error."},
    },
)
async def login(credentials: LoginSchema, db: DbTransactionDep) -> TokenResponseSchema:
    return await AuthService(db).login(credentials)


@auth_router.post(
    "/refresh",
    response_model=TokenResponseSchema,
    summary="Exchange a refresh token for a new pair",
    description=(
        "Validates the refresh JWT and issues a new access + refresh pair. "
        "The previous refresh token is **not** revoked in this template — "
        "wire Redis or a refresh-token store to add revocation."
    ),
    response_description="A new token pair.",
    responses={
        401: {"description": "Invalid, expired, or wrong-type token."},
    },
)
async def refresh(data: RefreshTokenSchema, db: DbTransactionDep) -> TokenResponseSchema:
    return await AuthService(db).refresh(data.refresh_token)


@auth_router.get(
    "/me",
    summary="Return the current user's JWT payload",
    description=(
        "Returns the decoded JWT payload for the bearer token in the "
        "`Authorization` header. Useful for clients to verify token validity "
        "and read claims (`sub`, `email`, `permissions`, `exp`)."
    ),
    response_description="The decoded JWT payload.",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "sub": "5b7e0c2a-2c8e-4a1a-9d2f-2bd5e0a9f1a4",
                        "email": "alice@example.com",
                        "type": "access",
                        "exp": 1746525600,
                    }
                }
            }
        },
        401: {"description": "Missing, malformed, or expired access token."},
    },
)
async def me(current_user: CurrentUserDep) -> dict:
    return current_user
