import logging
from datetime import datetime
from turtle import title
from typing import Optional

from backend.app.api.v1.models.messages import BundestagEinzelpersonAbstimmung
from backend.app.api.v1.models.queries import DateRange, DatetimeRange
from backend.app.crud.CRUDBundestag.crud_einzelperson_abstimmung import (
    CRUDBundestagEinzelpersonAbstimmung,
)
from backend.app.models.bundestag.abstimmung_model import BTEinzelpersonAbstimmung, BTPerson
from backend.app.services.common import ObjectNotFound

_logger = logging.getLogger(__name__)


class EinzelpersonAbstimmungService:
    def __init__(self):
        self.crud = CRUDBundestagEinzelpersonAbstimmung(BTEinzelpersonAbstimmung)

    def get_model(self):
        return BTEinzelpersonAbstimmung

    def get(self, id: int) -> Optional[BundestagEinzelpersonAbstimmung]:
        result = self.crud.read(id)
        return (
            BundestagEinzelpersonAbstimmung(
                id=result.id,
                person_id=result.person_id,
                abstimmung_id=result.abstimmung_id,
                vorname=result.person.name,
                nachname=result.person.surname,
                titel=result.person.title,
                fraktion=result.person.fraktion,
                vote=result.vote,
                image_url=result.person.image_url,
            )
            if result
            else None
        )

    def _build_base_filter_options(
        self,
        abstimmung_id: int | None = None,
        person_id: int | None = None,
    ) -> list:
        filters = []
        if abstimmung_id:
            filters.append(BTEinzelpersonAbstimmung.abstimmung_id == abstimmung_id)
        if person_id:
            filters.append(BTEinzelpersonAbstimmung.person_id == person_id)
        return filters

    def _build_person_filter_options(
        self,
        name: str | None = None,
        surname: str | None = None,
        fraktion: str | None = None,
    ) -> list:
        filters = []
        if name:
            filters.append(BTPerson.name == name)
        if surname:
            filters.append(BTPerson.surname == surname)
        if fraktion:
            filters.append(BTPerson.fraktion == fraktion)
        return filters

    def query_count(
        self,
        abstimmung_id: int | None = None,
        person_id: int | None = None,
        name: str | None = None,
        surname: str | None = None,
        fraktion: str | None = None,
    ) -> int:
        base_filters = self._build_base_filter_options(
            abstimmung_id=abstimmung_id,
            person_id=person_id,
        )

        person_filters = self._build_person_filter_options(
            name=name,
            surname=surname,
            fraktion=fraktion,
        )

        return self.crud.read_person_filtered_count(
            base_filters=base_filters,
            person_filters=person_filters,
        )

    def query(
        self,
        limit: int,
        skip: int = 0,
        abstimmung_id: int | None = None,
        person_id: int | None = None,
        name: str | None = None,
        surname: str | None = None,
        fraktion: str | None = None,
    ) -> list[BundestagEinzelpersonAbstimmung]:
        base_filters = self._build_base_filter_options(
            abstimmung_id=abstimmung_id,
            person_id=person_id,
        )

        person_filters = self._build_person_filter_options(
            name=name,
            surname=surname,
            fraktion=fraktion,
        )

        results = self.crud.read_person_filtered_multi(
            base_filters=base_filters, person_filters=person_filters, skip=skip, limit=limit
        )
        return [
            BundestagEinzelpersonAbstimmung(
                id=r.id,
                person_id=r.person_id,
                abstimmung_id=r.abstimmung_id,
                vorname=r.person.name,
                nachname=r.person.surname,
                titel=r.person.title,
                fraktion=r.person.fraktion,
                vote=r.vote,
                image_url=r.person.image_url,
            )
            for r in results
        ]
