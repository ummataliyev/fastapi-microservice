"""
Initialization of API routers.

This module aggregates all feature-specific routers
into a single `main_router` that is then mounted on the FastAPI application.
"""

from fastapi import APIRouter

from src.api.section import router as section_router
from src.api.complex import router as complex_router
from src.api.floor import router as floor_router
from src.api.building import router as building_router
from src.api.apartment import router as apartment_router
from src.api.plan_file import router as plan_file_router


routers = (
    complex_router,
    building_router,
    section_router,
    floor_router,
    apartment_router,
    plan_file_router,
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
