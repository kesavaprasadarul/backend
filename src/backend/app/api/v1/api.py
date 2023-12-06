"""API Router."""
from fastapi import APIRouter

from backend.app.api.v1.routers import plenarprotokolle
from backend.app.api.v1.routers import bundestag_top_topics, example

api_router = APIRouter()

api_router.include_router(example.router)
api_router.include_router(plenarprotokolle.router)
api_router.include_router(bundestag_top_topics.router)
