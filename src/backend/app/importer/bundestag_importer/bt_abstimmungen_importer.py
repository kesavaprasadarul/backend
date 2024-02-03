import datetime
import logging
from datetime import date
from typing import Iterator
from backend.app.core.config import settings
from backend.app.core.logging import configure_logging
from backend.app.crud.CRUDBundestag.crud_abstimmung import CRUD_BUNDESTAG_ABSTIMMUNG
from backend.app.crud.CRUDDIPBundestag.crud_drucksache import CRUD_DIP_DRUCKSACHE
from backend.app.facades.bundestag.model import (
    BundestagAbstimmung,
    BundestagAbstimmungUrl,
    BundestagEinzelpersonAbstimmung,
    Vote,
)
from backend.app.facades.bundestag.parameter_model import (
    BundestagAbstimmungenPointerParameter,
    BundestagAbstimmungParameter,
    BundestagRedeParameter,
)
from backend.app.facades.deutscher_bundestag.parameter_model import DrucksacheParameter
from backend.app.facades.util import ProxyList
from backend.app.importer.bundestag_importer.bt_importer import BTImporter
from backend.app.importer.dip_importer.dip_drucksache_text_importer import (
    DIPBundestagDrucksacheTextImporter,
)
from backend.app.models.bundestag.abstimmung_model import (
    BTAbstimmung,
    BTAbstimmungDrucksache,
    BTAbstimmungRedner,
    BTEinzelpersonAbstimmung,
    BTPerson,
    BTRede,
    BTFraktionAbstimmung,
)
from typing import Any, Generic, Iterator, MutableMapping, Optional, TypeVar

from backend.app.models.dip.drucksache_model import DIPDrucksache, DIPDrucksacheText

_logger = logging.getLogger(__name__)


class BTAbstimmungenImporter(
    BTImporter[BundestagAbstimmung, BundestagAbstimmungenPointerParameter, BTAbstimmung]
):
    def __init__(self, import_rede: bool = True, import_drucksache: bool = True):
        super().__init__(crud=CRUD_BUNDESTAG_ABSTIMMUNG)

        if import_drucksache:
            self.drucksache_import = DIPBundestagDrucksacheTextImporter(
                import_vorgaenge=True, import_vorgangspositionen=False
            )

        self.import_rede = import_rede

    def batch_upsert(
        self,
        params: Optional[BundestagAbstimmungenPointerParameter] = None,
        response_limit: int = 1000,
        proxy_list: ProxyList | None = None,
        upsert_batch_size: int = 100,
        **kwargs: Any,
    ):
        batch: list[BTAbstimmung] = []
        batch_number = 0
        for db_model in self.fetch_data(
            params=params, response_limit=response_limit, proxy_list=proxy_list, **kwargs
        ):
            batch.append(db_model)

            if len(batch) >= upsert_batch_size:
                _logger.debug(
                    f'Upserting batch {batch_number} into {db_model.__tablename__}-Table.'
                )
                self.crud.upsert_many(batch)
                batch = []
                batch_number += 1
                self.imported_count += upsert_batch_size

        if batch:
            _logger.debug(
                f'Upserting final batch ({batch_number}) into {batch[0].__tablename__}-Table.'
            )
            self.crud.create_or_update_multi(batch)
            self.imported_count += len(batch)

        _logger.debug(f'Imported {self.imported_count} {self.crud.model.__tablename__}.')

    def transform_model(
        self, data: BundestagAbstimmung, dip_drucksachen: list[DIPDrucksache] = []
    ) -> BTAbstimmung:
        bt_einzelabstimmungen = []

        bt_fraktionen = {}

        for einzelabstimmung in data.individual_votes:
            person = BTPerson(
                name=einzelabstimmung.name,
                surname=einzelabstimmung.surname,
                title=einzelabstimmung.title,
                fraktion=einzelabstimmung.fraktion,
                bundesland=einzelabstimmung.bundesland,
                biography_url=einzelabstimmung.biography_url.unicode_string(),
                image_url=einzelabstimmung.image_url.unicode_string()
                if einzelabstimmung.image_url
                else None,
            )

            bt_einzelabstimmungen.append(
                BTEinzelpersonAbstimmung(
                    vote=einzelabstimmung.vote,
                    person=person,
                )
            )

            if person.fraktion not in bt_fraktionen:
                bt_fraktionen[person.fraktion] = BTFraktionAbstimmung(
                    abstimmung_id=data.id,
                    fraktion=person.fraktion,
                    ja=0,
                    nein=0,
                    enthalten=0,
                    nicht_abgegeben=0,
                )

            if einzelabstimmung.vote == Vote.JA:
                bt_fraktionen[person.fraktion].ja += 1
            elif einzelabstimmung.vote == Vote.NEIN:
                bt_fraktionen[person.fraktion].nein += 1
            elif einzelabstimmung.vote == Vote.ENTHALTEN:
                bt_fraktionen[person.fraktion].enthalten += 1
            elif einzelabstimmung.vote == Vote.NICHTABGEGEBEN:
                bt_fraktionen[person.fraktion].nicht_abgegeben += 1

        bt_abstimmung_redner_dict = dict()

        for redner in data.redner:
            identifier = (
                redner.name,
                redner.surname,
                redner.title,
                redner.function,
            )
            rede = BTRede(
                bt_video_id=redner.video_id,
                video_url=redner.video_url.unicode_string(),
                text=redner.text,
            )
            if identifier not in bt_abstimmung_redner_dict:
                bt_redner = BTAbstimmungRedner(
                    name=redner.name,
                    surname=redner.surname,
                    title=redner.title,
                    function=redner.function,
                    image_url=redner.image_url.unicode_string(),
                )

                rede.abstimmung_redner = bt_redner
                bt_redner.reden.append(rede)
                bt_abstimmung_redner_dict[identifier] = bt_redner
            else:
                bt_redner = bt_abstimmung_redner_dict[identifier]
                rede.abstimmung_redner = bt_redner
                bt_redner.reden.append(rede)

        bt_abstimmung_redner = list(bt_abstimmung_redner_dict.values())

        bt_abstimmung_drucksachen = []
        for drucksache in data.drucksachen:
            dip_drucksache_rel = None
            for dip_drucksache in dip_drucksachen:
                if drucksache.drucksache_name == dip_drucksache.dokumentnummer:
                    dip_drucksache_rel = dip_drucksache
                    break

            bt_abstimmung_drucksachen.append(
                BTAbstimmungDrucksache(
                    drucksache_url=drucksache.url.unicode_string(),
                    drucksache_name=drucksache.drucksache_name,
                    dip_drucksache=dip_drucksache_rel,
                )
            )

        bt_abstimmung = BTAbstimmung(
            id=data.id,
            title=data.title,
            abstimmung_date=data.abstimmung_date,
            ja=data.ja,
            nein=data.nein,
            enthalten=data.enthalten,
            nicht_abgegeben=data.nicht_abgegeben,
            dachzeile=data.dachzeile,
            individual_votes=bt_einzelabstimmungen,
            drucksachen=bt_abstimmung_drucksachen,
            redner=bt_abstimmung_redner,
            fraktion_votes=list(bt_fraktionen.values()),
        )

        return bt_abstimmung

    def fetch_data(
        self,
        params: BundestagAbstimmungenPointerParameter | None = None,
        response_limit: int = 1000,
        proxy_list: ProxyList | None = None,
        **kwargs: Any,
    ) -> Iterator[BTAbstimmung]:
        existing_ids: set[int] | None = None
        if 'existing_ids' in kwargs:
            existing_ids = kwargs['existing_ids']

            if not isinstance(existing_ids, set):
                raise ValueError('existing_ids must be a set')

        for abstimmung_pointer in self.facade.get_bundestag_abstimmung_pointers(
            params=params, response_limit=response_limit
        ):
            if existing_ids is not None and abstimmung_pointer.abstimmung_id in existing_ids:
                _logger.debug(
                    f'Abstimmung with id {abstimmung_pointer.abstimmung_id} already exists in database. Skipping.'
                )
                continue
            individual_abstimmung_params = BundestagAbstimmungParameter(
                abstimmung_id=abstimmung_pointer.abstimmung_id
            )

            bt_abstimmung = self.facade.get_bundestag_abstimmung(
                params=individual_abstimmung_params
            )

            for bt_einzelabstimmung in self.facade.get_bundestag_abstimmung_individual_votes(
                params=individual_abstimmung_params
            ):
                bt_abstimmung.individual_votes.append(bt_einzelabstimmung)

            if self.import_rede:
                for redner in bt_abstimmung.redner:
                    rede_params = BundestagRedeParameter(video_id=redner.video_id)
                    bt_abstimmung_rede_text = self.facade.get_bundestag_rede_text(
                        params=rede_params
                    )
                    redner.text = bt_abstimmung_rede_text

            dip_drucksachen = []
            if self.drucksache_import and len(bt_abstimmung.drucksachen) > 0:
                drucksache_params = DrucksacheParameter(
                    dokumentnummer=[
                        drucksache.drucksache_name for drucksache in bt_abstimmung.drucksachen
                    ]
                )
                dip_drucksachen = [
                    dip_drucksache
                    for dip_drucksache in self.drucksache_import.fetch_data(
                        params=drucksache_params
                    )
                ]

            yield self.transform_model(bt_abstimmung, dip_drucksachen=dip_drucksachen)


def import_bt_abstimmungen(date_start: datetime.date, date_end: datetime.date, full: bool = False):
    _logger.info(f'Importing Abstimmungen from {date_start} to {date_end}.')
    importer = BTAbstimmungenImporter()
    params = BundestagAbstimmungenPointerParameter(date_start=date_start, date_end=date_end)

    if not full:
        existing_abstimmungen = importer.crud.read_all()

        existing_abstimmungen_ids = set(abstimmung.id for abstimmung in existing_abstimmungen)

        importer.import_data(
            params=params,
            response_limit=1000,
            upsert_batch_size=1,
            existing_ids=existing_abstimmungen_ids,
        )
    else:
        importer.import_data(params=params, response_limit=1000, upsert_batch_size=1)
    _logger.info(f'Imported Abstimmungen from {date_start} to {date_end}.')


if __name__ == '__main__':
    configure_logging()
    from datetime import date, timedelta

    import_bt_abstimmungen(
        date_start=date(2000, 1, 1), date_end=(date.today() + timedelta(weeks=1)), full=True
    )
