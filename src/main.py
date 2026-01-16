"""
Main entry point for the FastAPI application.
"""

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from src.api import main_router
from src.managers.middleware import MiddlewareManager
from src.core.settings import settings


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
            resource=Resource.create({"service.name": "fastapi-microservice"})
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

    app = FastAPI(
        title="Fastapi Micro Service",
        version="0.1.0",
        debug=settings.debug,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
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
    return "Service is running!"
