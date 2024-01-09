from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from logging import getLogger
from backend.app.importer.beschlussfassung_importer import FetchTypes, import_beschlussfassungen
from backend.app.importer.bundestag_importer.bt_abstimmungen_importer import import_bt_abstimmungen
from backend.app.importer.mandate_importer import import_mandate
from datetime import date, datetime, timedelta

_logger = getLogger(__name__)

app_scheduler = AsyncIOScheduler()


def startup_imports_job():
    """Startup event."""
    import_mandate()

    import_bt_abstimmungen(
        date_start=date(2023, 1, 1), date_end=(date.today() + timedelta(weeks=1))
    )

    # import_beschlussfassungen(
    #     fetch=FetchTypes.MISSING,
    #     date_start=date(2023, 1, 1),
    #     date_end=(date.today() + timedelta(weeks=1)),
    # )


def execution_listener(event):
    if event.exception:
        _logger.error(f"Job crashed: {event.job_id}")
        if event.job_id == 'startup_imports':
            app_scheduler.add_job(
                startup_imports_job,
                id=event.job_id,
                trigger='date',
                next_run_time=datetime.now() + timedelta(minutes=60),
            )
    else:
        _logger.info(f"Job finished: {event.job_id}")
        if event.job_id == 'startup_imports':
            pass
            # app_scheduler.add_job(
            #     import_beschlussfassungen,
            #     id='cron_import_abstimmungen',
            #     kwargs={'fetch': FetchTypes.NEW},
            #     trigger='cron',
            #     minute='*/15',
            #     max_instances=1,
            # )


def init_schedules():
    """Initialize scheduler."""
    app_scheduler.add_job(
        startup_imports_job,
        id='startup_imports',
        next_run_time=datetime.now(),
    )
    app_scheduler.add_listener(execution_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    app_scheduler.start()


def shutdown_scheduler():
    """Shutdown scheduler."""
    app_scheduler.shutdown(wait=True)
