import logging
from datetime import datetime
from typing import Optional

from backend.app.api.v1.models.messages import Abstimmung
from backend.app.api.v1.models.queries import DateRange, DatetimeRange
from backend.app.crud.CRUDApi.crud_abstimmung import CRUDAbstimmung
from backend.app.models.api.abstimmung_model import APIAbstimmung

_logger = logging.getLogger(__name__)


class AbstimmungService:
    def __init__(self):
        self.crud = CRUDAbstimmung(APIAbstimmung)

    def get_model(self):
        return APIAbstimmung

    def get(self, id: int) -> Optional[Abstimmung]:
        result = self.crud.read(id)
        _logger.info(result)
        return Abstimmung.model_validate(result) if result else None

    def _build_filter_options(
        self,
        datum: DateRange | None = None,
        aktualisiert: DatetimeRange | None = None,
    ) -> list:
        filters = []
        if datum:
            if datum.min:
                filters.append(APIAbstimmung.abstimmung_datum >= datum.min)
            if datum.max:
                filters.append(APIAbstimmung.abstimmung_datum <= datum.max)
        if aktualisiert:
            if aktualisiert.min:
                filters.append(APIAbstimmung.aktualisiert >= aktualisiert.min)
            if aktualisiert.max:
                filters.append(APIAbstimmung.aktualisiert <= aktualisiert.max)
        return filters

    def query_count(
        self,
        datum: DateRange | None = None,
        aktualisiert: DatetimeRange | None = None,
    ) -> int:
        filters = self._build_filter_options(
            datum=datum,
            aktualisiert=aktualisiert,
        )

        return self.crud.count(filters=filters)

    def query(
        self,
        limit: int,
        skip: int = 0,
        datum: DateRange | None = None,
        aktualisiert: DatetimeRange | None = None,
    ) -> list[Abstimmung]:
        filters = self._build_filter_options(
            datum=datum,
            aktualisiert=aktualisiert,
        )

        results = self.crud.read_multi(filters=filters, skip=skip, limit=limit)
        return [Abstimmung.model_validate(r) for r in results]
