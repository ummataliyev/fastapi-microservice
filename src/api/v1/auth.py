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

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post(
    "/register", response_model=TokenResponseSchema, status_code=status.HTTP_201_CREATED
)
async def register(data: UserCreateSchema, db: DbTransactionDep) -> TokenResponseSchema:
    return await AuthService(db).register(data)


@auth_router.post("/login", response_model=TokenResponseSchema)
async def login(credentials: LoginSchema, db: DbTransactionDep) -> TokenResponseSchema:
    return await AuthService(db).login(credentials)


@auth_router.post("/refresh", response_model=TokenResponseSchema)
async def refresh(data: RefreshTokenSchema, db: DbTransactionDep) -> TokenResponseSchema:
    return await AuthService(db).refresh(data.refresh_token)


@auth_router.get("/me")
async def me(current_user: CurrentUserDep) -> dict:
    return current_user
