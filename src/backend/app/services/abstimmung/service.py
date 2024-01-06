import logging
from datetime import datetime
from typing import Optional

from backend.app.api.v1.models.messages import BundestagAbstimmung, BundestagAbstimmungDrucksache
from backend.app.api.v1.models.queries import DateRange, DatetimeRange
from backend.app.crud.CRUDBundestag.crud_abstimmung import CRUDBundestagAbstimmung
from backend.app.models.bundestag.abstimmung_model import BTAbstimmung

_logger = logging.getLogger(__name__)


class AbstimmungService:
    def __init__(self):
        self.abstimmung_crud = CRUDBundestagAbstimmung(BTAbstimmung)

    def get_model(self):
        return BundestagAbstimmung

    def get(self, id: int) -> Optional[BundestagAbstimmung]:
        result = self.abstimmung_crud.read(id)

        return (
            BundestagAbstimmung(
                id=result.id,
                titel=result.title,
                abstimmung_date=result.abstimmung_date,
                ja=result.ja,
                nein=result.nein,
                enthalten=result.enthalten,
                nicht_abgegeben=result.nicht_abgegeben,
                dachzeile=result.dachzeile,
                drucksachen=[
                    BundestagAbstimmungDrucksache(
                        drucksache_url=drucksache.drucksache_url,
                        drucksache_name=drucksache.drucksache_name,
                    )
                    for drucksache in result.drucksachen
                ],
            )
            if result
            else None
        )

    def _build_filter_options(
        self,
        datum: DateRange | None = None,
    ) -> list:
        filters = []
        if datum:
            if datum.min:
                filters.append(BTAbstimmung.abstimmung_datum >= datum.min)
            if datum.max:
                filters.append(BTAbstimmung.abstimmung_datum <= datum.max)
        return filters

    def query_count(
        self,
        datum: DateRange | None = None,
    ) -> int:
        filters = self._build_filter_options(
            datum=datum,
        )

        return self.abstimmung_crud.count(filters=filters)

    def query(
        self,
        limit: int,
        skip: int = 0,
        datum: DateRange | None = None,
    ) -> list[BundestagAbstimmung]:
        filters = self._build_filter_options(
            datum=datum,
        )

        results = self.abstimmung_crud.read_multi(filters=filters, skip=skip, limit=limit)
        return [
            BundestagAbstimmung(
                id=r.id,
                titel=r.title,
                abstimmung_date=r.abstimmung_date,
                ja=r.ja,
                nein=r.nein,
                enthalten=r.enthalten,
                nicht_abgegeben=r.nicht_abgegeben,
                dachzeile=r.dachzeile,
                drucksachen=[
                    BundestagAbstimmungDrucksache(
                        drucksache_url=drucksache.drucksache_url,
                        drucksache_name=drucksache.drucksache_name,
                    )
                    for drucksache in r.drucksachen
                ],
            )
            for r in results
        ]
