"""
Initialization of API routers.
"""

from fastapi import APIRouter

from src.api.auth import router as auth_router
from src.api.health import router as health_router
from src.api.users import router as users_router
from src.api.ws import router as ws_router
from src.core.settings import settings

versioned_routers = (
    auth_router,
    users_router,
    ws_router,
)

api_v1_router = APIRouter(prefix=settings.api_prefix)
for router in versioned_routers:
    api_v1_router.include_router(router)

main_router = APIRouter()
main_router.include_router(health_router)
main_router.include_router(api_v1_router)

__all__ = (
    "auth_router",
    "users_router",
    "ws_router",
    "health_router",
    "api_v1_router",
    "main_router",
)
