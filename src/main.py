"""
Main entry point for the FastAPI application.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from src.api import main_router

from src.core.settings import settings

from src.db.redis.broker import redis_client

from src.managers.middleware import MiddlewareManager


def _setup_tracing(app: FastAPI) -> None:
    """
    Configure OpenTelemetry tracing with Jaeger exporter.
    Only initializes if tracing is enabled in settings.
    """
    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    trace.set_tracer_provider(
        TracerProvider(
            resource=Resource.create({
                "service.name": "fastapi-microservice"
            })
        )
    )

    jaeger_exporter = JaegerExporter(
        agent_host_name="jaeger",
        agent_port=6831,
    )

    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(jaeger_exporter)
    )

    FastAPIInstrumentor.instrument_app(app)


def create_application() -> FastAPI:
    """
    Create and configure FastAPI application
    """

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        """
        Lifespan.

        :param _: TODO - describe _.
        :type _: FastAPI
        :return: None.
        :raises Exception: If the operation fails.
        """
        yield
        if settings.db_provider.lower() == "mongo":
            from src.db.mongo.client import close_mongo_client
            await close_mongo_client()
        await redis_client.aclose()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url="/redoc" if settings.redoc_enabled else None,
        openapi_url="/openapi.json" if settings.openapi_enabled else None,
        lifespan=lifespan,
    )

    if settings.tracing_enabled:
        _setup_tracing(app)

    middleware_manager = MiddlewareManager(debug=settings.debug)
    middleware_manager.setup(app)

    app.include_router(main_router)

    return app


app = create_application()


@app.get(
    path="/",
    response_class=PlainTextResponse,
    summary="Service status",
    tags=["Status"],
)
async def root():
    """
    Root.

    :return: TODO - describe return value.
    :raises Exception: If the operation fails.
    """
    return f"{settings.app_name} is running!"
