"""API Router."""
from fastapi import APIRouter

from backend.app.api.api_v1.endpoints import example, get_bundestag_top_topics, plenarprotokolle

api_router = APIRouter()

api_router.include_router(example.router)
api_router.include_router(plenarprotokolle.router)
api_router.include_router(get_bundestag_top_topics.router)
