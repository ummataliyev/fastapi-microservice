from fastapi import APIRouter

api_v1_router = APIRouter(prefix="/template/api/v1")

# Include domain routers here, e.g.:
# from src.api.v1.items import items_router
# api_v1_router.include_router(items_router, tags=["items"])
