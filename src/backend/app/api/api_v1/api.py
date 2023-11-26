"""API Router."""
from fastapi import APIRouter

from backend.app.api.api_v1.endpoints import example, plenarprotokolle

api_router = APIRouter()

api_router.include_router(example.router)
api_router.include_router(plenarprotokolle.router)
