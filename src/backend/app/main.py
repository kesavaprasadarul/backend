"""Entry point for FastAPI including API routers (endpoints)."""
from fastapi import FastAPI

from backend.app.core.config import settings
from backend.app.core.logging import configure_logging

configure_logging()

app = FastAPI(title="backend", openapi_url=f"{settings.API_V1_STR}/openapi.json")
