import logging
from datetime import datetime
from typing import Optional

from backend.app.api.v1.models.messages import BundestagTopTopic
from backend.app.api.v1.models.queries import DateRange, DatetimeRange
from backend.app.crud.CRUDApi.crud_top_topics import CRUD_TOP_TOPICS
from backend.app.models.api.top_topics_model import TopTopics

_logger = logging.getLogger(__name__)


class BundestagTopTopicsService:
    def __init__(self):
        self.crud = CRUD_TOP_TOPICS

    def get_model(self):
        return TopTopics

    def get(self, id: int) -> Optional[BundestagTopTopic]:
        result = self.crud.read(id)
        _logger.info(result)
        return BundestagTopTopic.model_validate(result) if result else None

    def _build_filter_options(
        self,
        month: int | None,
        year: int | None,
        election_period: int | None,
    ) -> list:
        filters = []
        if month and year and not election_period:
            filters.append(TopTopics.month == month)
            filters.append(TopTopics.year == year)
            filters.append(TopTopics.election_period == 0)
        if year and not month and not election_period:
            filters.append(TopTopics.month == None)
            filters.append(TopTopics.year == year)
            filters.append(TopTopics.election_period == 0)
        if election_period and not year and not month:
            filters.append(TopTopics.month == 0)
            filters.append(TopTopics.year == 0)
            filters.append(TopTopics.election_period == election_period)

        return filters

    def query(
        self,
        month: int | None,
        year: int | None,
        election_period: int | None,
    ) -> list[BundestagTopTopic]:
        filters = self._build_filter_options(
            month=month,
            year=year,
            election_period=election_period,
        )

        results = self.crud.read_multi(filters=filters)
        return [BundestagTopTopic.model_validate(r) for r in results]
