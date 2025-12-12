"""
Main entry point for the FastAPI application.

This file creates the FastAPI app instance, configures metadata like
title and version, and includes the main API router with all routes.
Swagger (docs) and ReDoc endpoints are also configured here.
"""

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from src.api import main_router


trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create(
            {
                "service.name":
                "fastapi-microservice"
            }
        )
    )
)
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))

app = FastAPI(
    title="Fastapi Micro Service",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

FastAPIInstrumentor.instrument_app(app)


@app.get(
        path="/",
        response_class=PlainTextResponse,
        summary="Service status",
        tags=["Status"]
    )
async def root():
    """
    Root endpoint for health/status check.

    Returns:
        Plain text status message
    """
    return "Service is running!"


app.include_router(main_router)
"""
Include the main API router.

:return: None. Registers all routes from `main_router` under the app instance.
"""


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
