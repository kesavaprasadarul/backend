import logging
from datetime import datetime
from typing import Optional

from backend.app.api.v1.models.messages import BundestagAbstimmungRedner, BundestagRede
from backend.app.api.v1.models.queries import DateRange, DatetimeRange
from backend.app.crud.CRUDBundestag.crud_abstimmung_redner import CRUDBundestagAbstimmungRedner
from backend.app.models.bundestag.abstimmung_model import BTAbstimmungRedner

_logger = logging.getLogger(__name__)


class AbstimmungRednerService:
    def __init__(self):
        self.abstimmung_redner_crud = CRUDBundestagAbstimmungRedner(BTAbstimmungRedner)

    def get_model(self):
        return BundestagAbstimmungRedner

    def get(self, id: int) -> Optional[BundestagAbstimmungRedner]:
        result = self.abstimmung_redner_crud.read(id)

        return (
            BundestagAbstimmungRedner(
                id=result.id,
                abstimmung_id=result.abstimmung_id,
                full_name=(result.title + " " + result.name + " " + result.surname).strip()
                if result.title
                else (result.name + " " + result.surname).strip(),
                function=result.function,
                image_url=result.image_url,
                reden=[
                    BundestagRede(
                        bt_video_id=rede.bt_video_id, video_url=rede.video_url, text=rede.text
                    )
                    for rede in result.reden
                ],
            )
            if result
            else None
        )

    def _build_filter_options(
        self,
        name: str | None = None,
        surname: str | None = None,
        abstimmung_id: list[int] | None = None,
    ) -> list:
        filters = []
        if name:
            filters.append(BTAbstimmungRedner.name == name)
        if surname:
            filters.append(BTAbstimmungRedner.surname == surname)
        if abstimmung_id:
            filters.append(BTAbstimmungRedner.abstimmung_id.in_(abstimmung_id))
        return filters

    def query_count(
        self,
        name: str | None = None,
        surname: str | None = None,
        abstimmung_id: list[int] | None = None,
    ) -> int:
        filters = self._build_filter_options(
            name=name,
            surname=surname,
            abstimmung_id=abstimmung_id,
        )

        return self.abstimmung_redner_crud.count(filters=filters)

    def query(
        self,
        limit: int,
        skip: int = 0,
        name: str | None = None,
        surname: str | None = None,
        abstimmung_id: list[int] | None = None,
    ) -> list[BundestagAbstimmungRedner]:
        filters = self._build_filter_options(
            name=name,
            surname=surname,
            abstimmung_id=abstimmung_id,
        )

        results = self.abstimmung_redner_crud.read_multi(filters=filters, skip=skip, limit=limit)
        return [
            BundestagAbstimmungRedner(
                id=r.id,
                abstimmung_id=r.abstimmung_id,
                full_name=(r.title + " " + r.name + " " + r.surname).strip()
                if r.title
                else (r.name + " " + r.surname).strip(),
                function=r.function,
                image_url=r.image_url,
                reden=[
                    BundestagRede(
                        bt_video_id=rede.bt_video_id, video_url=rede.video_url, text=rede.text
                    )
                    for rede in r.reden
                ],
            )
            for r in results
        ]
