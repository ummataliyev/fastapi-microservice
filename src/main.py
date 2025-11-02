"""
Main entry point for the FastAPI application.

This file creates the FastAPI app instance, configures metadata like
title and version, and includes the main API router with all routes.
Swagger (docs) and ReDoc endpoints are also configured here.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import main_router


app = FastAPI(
    title="Fastapi Micro Service",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)
"""
FastAPI application configured with metadata.

:param title: Title of the API.
:param version: Version string of the API.
:param root_path: Root path for all API routes.
"""

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
