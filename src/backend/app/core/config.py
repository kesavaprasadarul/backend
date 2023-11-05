"""Configuration of Settings."""
import pydantic as pyd
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Containing settings by loading environment variables."""

    # GENERAL
    API_V1_STR: str = pyd.Field(default="/api/v1")

    # PostgreSQL Database
    POSTGRES_DB: str = pyd.Field(default="fastapi")
    POSTGRES_PASSWORD: str = pyd.Field(default="password")
    POSTGRES_SERVER: str = pyd.Field(default="db")
    POSTGRES_USER: str = pyd.Field(default="admin")


settings = Settings()
