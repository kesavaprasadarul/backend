"""Logging setup with daiquiri."""
import logging
import sys

import daiquiri
import daiquiri.formatter
from backend.app.utils import get_project_root


def configure_logging():
    daiquiri.setup(
        level=logging.INFO,
        outputs=[
            daiquiri.output.Stream(sys.stdout),
            daiquiri.output.File(
                str(get_project_root() / "logs" / "backend.log"),
                formatter=daiquiri.formatter.ColorFormatter(
                    fmt="%(asctime)s [%(process)d] [%(levelname)s] %(name)s -> %(message)s"
                ),
            ),
        ],
    )

    _logger = daiquiri.getLogger(__name__)
