"""Contains endpoints for importing PLENARPROTOKOLLE from DIP Bundestag API with DIP Bundestag facade."""
import logging

import fastapi

from backend.app.api.v1.models.responses import BundestagTopTopicsApiResponse
from backend.app.app_logic.landing_page.create_bundestag_top_topics import (
    create_bundestag_top_topics,
)
from backend.app.core.bundestag_ressorts import BUNDESTAG_RESSORTS
from backend.app.services.bundestag_top_topics.service import BundestagTopTopicsService

_logger = logging.getLogger(__name__)

router = fastapi.APIRouter(prefix="/bundestag_top_topics", tags=["bundestag-top-topics"])


@router.get(path='/', response_model=BundestagTopTopicsApiResponse)
def get_bundestag_top_topics(
    month: int | None = None,
    year: int | None = None,
    election_period: int | None = None,
    service: BundestagTopTopicsService = fastapi.Depends(BundestagTopTopicsService),
):
    bundestag_top_topics = service.query(
        month=month,
        year=year,
        election_period=election_period,
    )

    top_topics_by_ressort: dict[str, list[list]] = {}

    for ressort in BUNDESTAG_RESSORTS:
        top_topics_by_ressort[ressort] = [
            [top_topic.word, top_topic.value]
            for top_topic in bundestag_top_topics
            if top_topic.ressort == ressort
        ]

    api_response = BundestagTopTopicsApiResponse(
        month=month, year=year, election_period=election_period, top_topics=top_topics_by_ressort
    )

    return api_response


@router.post(path='/', response_model=BundestagTopTopicsApiResponse)
def post_bundestag_top_topics(
    month: int | None = None, year: int | None = None, election_period: int | None = None
):
    top_topics_per_ressort: dict[str, list[list]] = create_bundestag_top_topics(
        month, year, election_period
    )

    return BundestagTopTopicsApiResponse(
        month=month, year=year, election_period=election_period, top_topics=top_topics_per_ressort
    )
