"""Entry point for FastAPI including API routers (endpoints)."""
import time
from contextlib import asynccontextmanager
import uvicorn

from logging import getLogger
from sched import scheduler

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, middleware
from backend.app.api.v1.api import api_router
from backend.app.core.config import settings
from backend.app.core.logging import configure_logging

from backend.app.scheduler import init_schedules, shutdown_scheduler

_logger = getLogger(__name__)

configure_logging()

importer = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup event."""
    _logger.info("Starting up...")

    if importer:
        init_schedules()

    yield

    shutdown_scheduler()


origins = [
    "http://localhost:3000",
    "http://localhost:80",
    "http://localhost",
]


app = FastAPI(title="backend", openapi_url=f"{settings.API_V1_STR}/openapi.json", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=f"{settings.API_V1_STR}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
