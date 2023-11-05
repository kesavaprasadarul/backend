"""Logging setup with daiquiri."""
import logging
import sys

import daiquiri


def configure_logging():
    daiquiri.setup(
        level=logging.INFO,
        outputs=[
            daiquiri.output.Stream(sys.stdout),
        ],
    )

    _logger = daiquiri.getLogger(__name__)
