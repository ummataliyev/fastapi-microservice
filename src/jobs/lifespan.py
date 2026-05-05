from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from src.core.observability.logging import get_logger
from src.core.timezone import timezonetash

logger = get_logger(__name__)

scheduler = AsyncIOScheduler(timezone=timezonetash)


@asynccontextmanager
async def combined_lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Combined lifespan:
    - Starts APScheduler.
    - Add cron jobs here, e.g.:
          from src.services.things import register_things_sync_job
          register_things_sync_job(scheduler)
    """
    logger.info("Starting APScheduler")
    scheduler.start()
    try:
        yield
    finally:
        logger.info("Stopping APScheduler")
        scheduler.shutdown(wait=False)
