from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.exceptions.services.base import BaseServiceException


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(BaseServiceException)
    async def service_exception_handler(_: Request, exc: BaseServiceException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "type": exc.__class__.__name__},
        )
