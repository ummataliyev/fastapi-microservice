from fastapi import APIRouter

from src.api.v1.auth import auth_router
from src.api.v1.items import items_router
from src.api.v1.users import users_router

api_v1_router = APIRouter(prefix="/template/api/v1")
api_v1_router.include_router(auth_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(items_router)
