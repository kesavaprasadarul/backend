"""Contains endpoints for importing PLENARPROTOKOLLE from DIP Bundestag API with DIP Bundestag facade."""
import logging

import fastapi
import pydantic as pyd

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
def get_bundestag_top_topics(month: int | None = None, year: int | None = None, election_period: int | None = None):

    top_topics_per_ressort: dict[str, list[list]] = get_bundestag_top_topics_for_month(month, year)

    return GetBundestagTopTopicsApiResponse(
        month=month, year=year, election_period=election_period, top_topics=top_topics_per_ressort
    )


class GetBundestagTopTopicsApiResponse(pyd.BaseModel):
    """Pydantic model for output."""

    month: int | None = pyd.Field(default=None)
    year: int | None = pyd.Field(default=None)
    election_period: int | None = pyd.Field(default=None)
    top_topics: dict[str, list] | None = pyd.Field(default=None)
