"""Contains endpoints for importing PLENARPROTOKOLLE from DIP Bundestag API with DIP Bundestag facade."""
import logging

import fastapi

from backend.app.api.v1.models.responses import BundestagTopTopicsApiResponse
from backend.app.app_logic.landing_page.get_bundestag_top_topics import (
    get_bundestag_top_topics_for_month,
)

_logger = logging.getLogger(__name__)

router = fastapi.APIRouter(prefix="/bundestag_top_topics", tags=["bundestag-top-topics"])


@router.get(path='/', response_model=BundestagTopTopicsApiResponse)
def get_bundestag_top_topics(
    month: int | None = None, year: int | None = None, election_period: int | None = None
):
    top_topics_per_ressort: dict[str, list[list]] = get_bundestag_top_topics_for_month(month, year)

    return BundestagTopTopicsApiResponse(
        month=month, year=year, election_period=election_period, top_topics=top_topics_per_ressort
    )
