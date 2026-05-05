from contextlib import asynccontextmanager
from typing import Annotated, AsyncIterator

import sentry_sdk
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi_pagination import add_pagination
from prometheus_fastapi_instrumentator import Instrumentator
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from src.api.dependencies.docs import get_current_user_for_docs
from src.api.handlers.exceptions import register_exception_handlers
from src.api.v1 import api_v1_router
from src.core.observability.logging import get_logger, setup_logging
from src.core.settings import settings
from src.jobs.lifespan import combined_lifespan

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    async with combined_lifespan(app):
        yield


def create_application() -> FastAPI:
    setup_logging()
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)

    if settings.sentry_dsn:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.app_env,
            integrations=[SqlalchemyIntegration()],
            traces_sample_rate=0.1,
        )

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    Instrumentator().instrument(app).expose(
        app, endpoint="/template/metrics", include_in_schema=False
    )
    app.include_router(api_v1_router)
    register_exception_handlers(app)
    add_pagination(app)

    @app.get("/template/health", include_in_schema=False)
    async def health() -> dict:
        return {
            "status": "ok",
            "service": settings.app_name,
            "version": settings.app_version,
        }

    @app.get("/template/openapi.json", include_in_schema=False)
    async def openapi(_: Annotated[str, Depends(get_current_user_for_docs)]) -> dict:
        return get_openapi(title=app.title, version=app.version, routes=app.routes)

    @app.get("/template/docs", include_in_schema=False)
    async def docs(_: Annotated[str, Depends(get_current_user_for_docs)]):
        return get_swagger_ui_html(openapi_url="/template/openapi.json", title=app.title)

    return app


app = create_application()
