"""API Router."""
from fastapi import APIRouter

from backend.app.api.v1.routers import (
    beschlussfassung,
    bundestag_top_topics,
    example,
    abstimmung,
    einzelperson_abstimmung,
    abstimmung_redner,
)

api_router = APIRouter()

api_router.include_router(example.router)
api_router.include_router(beschlussfassung.router)
api_router.include_router(bundestag_top_topics.router)
api_router.include_router(abstimmung.router)
api_router.include_router(abstimmung_redner.router)
api_router.include_router(einzelperson_abstimmung.router)
