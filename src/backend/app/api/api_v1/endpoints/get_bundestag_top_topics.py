"""Contains endpoints for importing PLENARPROTOKOLLE from DIP Bundestag API with DIP Bundestag facade."""
import logging

import fastapi

from backend.app.app_logic.landing_page.get_bundestag_top_topics import (
    get_bundestag_top_topics_for_month,
)
from backend.app.importer.dip_plenarprotokoll_importer import DIPBundestagPlenarprotokollImporter

_logger = logging.getLogger(__name__)

router = fastapi.APIRouter()


@router.get(
    "/bundestag_top_topics",
    tags=["bundestag-top-topics"],
)
def get_bundestag_top_topics(month: int, year: int):
    return get_bundestag_top_topics_for_month(month, year)
