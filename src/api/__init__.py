"""
Initialization of API routers.

This module aggregates all feature-specific routers
into a single `main_router` that is then mounted on the FastAPI application.
"""

from fastapi import APIRouter

from src.api.users import router as users_router


routers = (
    users_router,
)

main_router = APIRouter()
"""
Main APIRouter instance.

:return: Aggregated router that includes all sub-routers.
"""

for router in routers:
    main_router.include_router(router)
"""
Loop through all routers and register them with the main router.

:param routers: Tuple of APIRouter instances to include.
:return: None
"""
