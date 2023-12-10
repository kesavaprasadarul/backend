"""Entry point for FastAPI including API routers (endpoints)."""
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from logging import getLogger
from sched import scheduler

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI

from backend.app.api.v1.api import api_router
from backend.app.core.config import settings
from backend.app.core.logging import configure_logging
from backend.app.importer.abstimmung_importer import FetchTypes, import_abstimmungen

_logger = getLogger(__name__)

configure_logging()

app_scheduler = AsyncIOScheduler()


def execution_listener(event):
    if event.exception:
        _logger.error(f"Job crashed: {event.job_id}")
    else:
        _logger.info(f"Job finished: {event.job_id}")
        if event.job_id == 'init_import_abstimmungen':
            app_scheduler.add_job(
                import_abstimmungen,
                id='cron_import_abstimmungen',
                kwargs={'fetch': FetchTypes.NEW},
                trigger='cron',
                minute='*/15',
                max_instances=1,
            )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup event."""

    app_scheduler.add_job(
        import_abstimmungen,
        id='init_import_abstimmungen',
        kwargs={
            'fetch': FetchTypes.MISSING,
            'date_start': datetime(2023, 12, 1),
            'date_end': (datetime.now() + timedelta(weeks=1)),
        },
        next_run_time=datetime.now(),
    )

    app_scheduler.add_listener(execution_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    app_scheduler.start()

    yield

    app_scheduler.shutdown(wait=True)


app = FastAPI(title="backend", openapi_url=f"{settings.API_V1_STR}/openapi.json", lifespan=lifespan)

app.include_router(api_router, prefix=f"{settings.API_V1_STR}")
