"""Logging setup with daiquiri."""
import datetime
import logging
import sys

import daiquiri
import daiquiri.formatter

from backend.app.utils import get_project_root


def configure_logging():
    daiquiri.setup(
        level=logging.DEBUG,
        outputs=[
            daiquiri.output.Stream(sys.stdout, level=logging.INFO),
            daiquiri.output.TimedRotatingFile(
                str(get_project_root() / "logs" / "debug.log"),
                formatter=daiquiri.formatter.ColorFormatter(
                    fmt="%(asctime)s [%(process)d] [%(levelname)s] %(name)s -> %(message)s"
                ),
                level=logging.DEBUG,
                interval=datetime.timedelta(hours=1),
            ),
            daiquiri.output.TimedRotatingFile(
                str(get_project_root() / "logs" / "info.log"),
                formatter=daiquiri.formatter.ColorFormatter(
                    fmt="%(asctime)s [%(process)d] [%(levelname)s] %(name)s -> %(message)s"
                ),
                level=logging.INFO,
                interval=datetime.timedelta(hours=1),
            ),
        ],
    )

    _logger = daiquiri.getLogger(__name__)
