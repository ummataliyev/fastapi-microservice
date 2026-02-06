"""
Health probes for container orchestration and uptime monitoring.
"""

from fastapi import status
from fastapi import Response
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from sqlalchemy import text

from src.db.redis.broker import redis_client

from src.api.dependencies import DbReadonlyDep

from src.core.settings import settings
from src.core.observability.metrics import render_metrics


router = APIRouter(tags=["Health"])


@router.get("/health", status_code=status.HTTP_200_OK, summary="General health")
async def health() -> dict[str, str]:
    """
    Health.

    :return: TODO - describe return value.
    :rtype: dict[str, str]
    :raises Exception: If the operation fails.
    """
    return {"status": "ok"}


@router.get("/live", status_code=status.HTTP_200_OK, summary="Liveness probe")
async def live() -> dict[str, str]:
    """
    Live.

    :return: TODO - describe return value.
    :rtype: dict[str, str]
    :raises Exception: If the operation fails.
    """
    return {"status": "alive"}


@router.get("/ready", summary="Readiness probe")
async def ready(db: DbReadonlyDep) -> JSONResponse:
    """
    Ready.

    :param db: TODO - describe db.
    :type db: DbReadonlyDep
    :return: TODO - describe return value.
    :rtype: JSONResponse
    :raises Exception: If the operation fails.
    """
    db_state = "ok"
    redis_state = "ok"
    provider = settings.db_provider.lower()

    try:
        if provider == "mongo":
            await db.session.command("ping")
        else:
            await db.session.execute(text("SELECT 1"))
    except Exception:
        db_state = "failed"

    try:
        await redis_client.ping()
    except Exception:
        redis_state = "failed"

    is_ready = db_state == "ok" and redis_state == "ok"
    status_value = "ready" if is_ready else "degraded"
    status_code = status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(
        status_code=status_code,
        content={
            "status": status_value,
            "database_type": provider,
            "checks": {"database": db_state, "redis": redis_state},
        },
    )


@router.get("/metrics", include_in_schema=False)
async def metrics() -> Response:
    """
    Metrics.

    :return: TODO - describe return value.
    :rtype: Response
    :raises Exception: If the operation fails.
    """
    payload, content_type = render_metrics()
    return Response(content=payload, media_type=content_type)
