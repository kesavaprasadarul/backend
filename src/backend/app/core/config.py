"""Configuration of Settings."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Containing settings by loading environment variables."""

    # GENERAL
    API_V1_STR: str = "/api/v1"


settings = Settings()
