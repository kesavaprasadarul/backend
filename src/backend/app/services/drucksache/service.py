import logging
from datetime import datetime
from typing import Optional

from backend.app.api.v1.models.messages import Drucksache, Verkuendung, Vorgang
from backend.app.api.v1.models.queries import DateRange, DatetimeRange
from backend.app.crud.CRUDDIPBundestag.crud_drucksache import CRUDDIPDrucksache
from backend.app.models.dip.drucksache_model import DIPDrucksache

_logger = logging.getLogger(__name__)


class DrucksacheService:
    def __init__(self):
        self.crud = CRUDDIPDrucksache(DIPDrucksache)

    def get_model(self):
        return DIPDrucksache

    def get(self, id: int) -> Optional[Drucksache]:
        result = self.crud.read(id)
        return (
            Drucksache(
                id=result.id,
                drucksachetyp=result.drucksachetyp,
                drucksache_name=result.dokumentnummer,
                pdf_url=result.fundstelle.pdf_url,
                titel=result.titel,
                datum=result.datum,
                ressorts=[r.ressort for r in result.ressort],
                vorgaenge=[
                    Vorgang(
                        vorgang_id=v.id,
                        vorgangstyp=v.vorgangstyp,
                        datum=v.datum,
                        beratungsstand=v.beratungsstand,
                        titel=v.titel,
                        abstract=v.abstract,
                        sachgebiet=v.sachgebiet if v.sachgebiet else [],
                        verkuendungen=[
                            Verkuendung(
                                id=ve.id,
                                fundstelle=ve.fundstelle,
                                pdf_url=ve.pdf_url,
                                typ=ve.einleitungstext,
                            )
                            for ve in v.verkuendung
                        ],
                        deskriptoren=[d.name for d in v.deskriptor],
                        initiatoren=v.initiative if v.initiative else [],
                    )
                    for v in result.vorgaenge
                ],
            )
            if result
            else None
        )

    def _build_filter_options(
        self,
        datum: DateRange | None = None,
        aktualisiert: DatetimeRange | None = None,
        drucksache_ids: list[int] | None = None,
    ) -> list:
        filters = []
        if datum:
            if datum.min:
                filters.append(DIPDrucksache.datum >= datum.min)
            if datum.max:
                filters.append(DIPDrucksache.datum <= datum.max)
        if aktualisiert:
            if aktualisiert.min:
                filters.append(DIPDrucksache.aktualisiert >= aktualisiert.min)
            if aktualisiert.max:
                filters.append(DIPDrucksache.aktualisiert <= aktualisiert.max)
        if drucksache_ids:
            filters.append(DIPDrucksache.id.in_(drucksache_ids))
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
        drucksache_ids: list[int] | None = None,
    ) -> list[Drucksache]:
        filters = self._build_filter_options(
            datum=datum,
            aktualisiert=aktualisiert,
            drucksache_ids=drucksache_ids,
        )

        results = self.crud.read_multi(filters=filters, skip=skip, limit=limit)
        return [
            Drucksache(
                id=result.id,
                drucksachetyp=result.drucksachetyp,
                drucksache_name=result.dokumentnummer,
                pdf_url=result.fundstelle.pdf_url,
                titel=result.titel,
                datum=result.datum,
                ressorts=[r.titel for r in result.ressort],
                vorgaenge=[
                    Vorgang(
                        vorgang_id=v.id,
                        vorgangstyp=v.vorgangstyp,
                        datum=v.datum,
                        beratungsstand=v.beratungsstand,
                        titel=v.titel,
                        abstract=v.abstract,
                        sachgebiet=v.sachgebiet if v.sachgebiet else [],
                        verkuendungen=[
                            Verkuendung(
                                id=ve.id,
                                fundstelle=ve.fundstelle,
                                pdf_url=ve.pdf_url,
                                typ=ve.einleitungstext,
                            )
                            for ve in v.verkuendung
                        ],
                        deskriptoren=[d.name for d in v.deskriptor],
                        initiatoren=v.initiative if v.initiative else [],
                    )
                    for v in result.vorgaenge
                ],
            )
            for result in results
        ]
