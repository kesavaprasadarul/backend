"""Contains endpoints for importing PLENARPROTOKOLLE from DIP Bundestag API with DIP Bundestag facade."""
import logging

import fastapi

from backend.app.api.v1.models.responses import BundestagTopTopicsApiResponse
from backend.app.app_logic.landing_page.create_bundestag_top_topics import create_bundestag_top_topics

_logger = logging.getLogger(__name__)

router = fastapi.APIRouter(prefix="/bundestag_top_topics", tags=["bundestag-top-topics"])


@router.get(path='/')
def get_bundestag_top_topics(
    month: int | None = None, year: int | None = None, election_period: int | None = None
):
    pass
    # top_topics_per_ressort: dict[str, list[list]] = get_bundestag_top_topics_for_month(month, year)

    # return BundestagTopTopicsApiResponse(
    #     month=month, year=year, election_period=election_period, top_topics=top_topics_per_ressort
    # )


@router.post(path='/', response_model=BundestagTopTopicsApiResponse)
def post_bundestag_top_topics(
    month: int | None = None, year: int | None = None, election_period: int | None = None
):
    top_topics_per_ressort: dict[str, list[list]] = create_bundestag_top_topics(month, year, election_period)

    return BundestagTopTopicsApiResponse(
        month=month, year=year, election_period=election_period, top_topics=top_topics_per_ressort
    )
