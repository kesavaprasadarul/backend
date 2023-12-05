import json
import logging
import logging.config
import os

from pathlib import Path


def get_project_root() -> Path:
    """Returns project root folder."""
    return Path(__file__).parent.parent


def get_data_folder() -> Path:
    """Returns data folder."""
    return get_project_root() / "data"
