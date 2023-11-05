"""API Router."""
from fastapi import APIRouter

from backend.app.api.api_v1.endpoints import example

api_router = APIRouter()

api_router.include_router(example.router)
