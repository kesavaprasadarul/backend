"""Entry point for FastAPI including API routers (endpoints)."""
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, date
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
from backend.app.importer.mandate_importer import import_mandate

_logger = getLogger(__name__)

configure_logging()

app_scheduler = AsyncIOScheduler()


def execution_listener(event):
    if event.exception:
        _logger.error(f"Job crashed: {event.job_id}")
        if event.job_id == 'startup_imports':
            app_scheduler.add_job(
                event.job.func,
                id=event.job_id,
                kwargs=event.job.kwargs,
                trigger='date',
                next_run_time=datetime.now() + timedelta(minutes=60),
            )
    else:
        _logger.info(f"Job finished: {event.job_id}")
        if event.job_id == 'startup_imports':
            app_scheduler.add_job(
                import_abstimmungen,
                id='cron_import_abstimmungen',
                kwargs={'fetch': FetchTypes.NEW},
                trigger='cron',
                minute='*/15',
                max_instances=1,
            )


def startup_imports_job():
    """Startup event."""
    import_mandate()

    import_abstimmungen(
        fetch=FetchTypes.MISSING,
        date_start=date(2023, 1, 1),
        date_end=(date.today() + timedelta(weeks=1)),
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup event."""

    app_scheduler.add_job(
        startup_imports_job,
        id='startup_imports',
        next_run_time=datetime.now(),
    )
    app_scheduler.add_listener(execution_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    app_scheduler.start()

    yield

    app_scheduler.shutdown(wait=True)


app = FastAPI(title="backend", openapi_url=f"{settings.API_V1_STR}/openapi.json", lifespan=lifespan)

app.include_router(api_router, prefix=f"{settings.API_V1_STR}")
