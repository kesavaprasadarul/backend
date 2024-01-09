import logging
from datetime import datetime
from typing import Optional

from backend.app.api.v1.models.messages import Beschlussfassung
from backend.app.api.v1.models.queries import DateRange, DatetimeRange
from backend.app.crud.CRUDApi.crud_beschlussfassung import CRUDBeschlussfassung
from backend.app.models.api.beschlussfassung_model import APIBeschlussfassung

_logger = logging.getLogger(__name__)


class BeschlussfassungService:
    def __init__(self):
        self.crud = CRUDBeschlussfassung(APIBeschlussfassung)

    def get_model(self):
        return APIBeschlussfassung

    def get(self, id: int) -> Optional[Beschlussfassung]:
        result = self.crud.read(id)
        return Beschlussfassung.model_validate(result) if result else None

    def _build_filter_options(
        self,
        datum: DateRange | None = None,
        aktualisiert: DatetimeRange | None = None,
    ) -> list:
        filters = []
        if datum:
            if datum.min:
                filters.append(APIBeschlussfassung.abstimmung_datum >= datum.min)
            if datum.max:
                filters.append(APIBeschlussfassung.abstimmung_datum <= datum.max)
        if aktualisiert:
            if aktualisiert.min:
                filters.append(APIBeschlussfassung.aktualisiert >= aktualisiert.min)
            if aktualisiert.max:
                filters.append(APIBeschlussfassung.aktualisiert <= aktualisiert.max)
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
    ) -> list[Beschlussfassung]:
        filters = self._build_filter_options(
            datum=datum,
            aktualisiert=aktualisiert,
        )

        results = self.crud.read_multi(filters=filters, skip=skip, limit=limit)
        return [Beschlussfassung.model_validate(r) for r in results]
