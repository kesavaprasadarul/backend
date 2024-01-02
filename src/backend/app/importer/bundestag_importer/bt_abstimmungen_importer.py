from backend.app.facades.bundestag.parameter_model import (
    BundestagAbstimmungenPointerParameter,
    BundestagAbstimmungParameter,
)
from backend.app.facades.bundestag.model import (
    BundestagAbstimmungUrl,
    BundestagAbstimmung,
    BundestagEinzelpersonAbstimmung,
    Vote,
)
from backend.app.crud.CRUDBundestag.crud_abstimmung import CRUD_BUNDESTAG_ABSTIMMUNG
from backend.app.importer.bundestag_importer.bt_importer import BTImporter
from backend.app.models.bundestag.abstimmung_model import (
    BTAbstimmung,
    BTPerson,
    BTEinzelpersonAbstimmung,
    BTAbstimmungRedner,
    BTAbstimmungDrucksache,
)
from backend.app.core.config import settings
from backend.app.core.logging import configure_logging
from backend.app.facades.util import ProxyList
from datetime import date
from typing import Iterator
import logging

_logger = logging.getLogger(__name__)


class BTAbstimmungenImporter(
    BTImporter[BundestagAbstimmung, BundestagAbstimmungenPointerParameter, BTAbstimmung]
):
    def __init__(self):
        super().__init__(crud=CRUD_BUNDESTAG_ABSTIMMUNG)

    def transform_model(self, data: BundestagAbstimmung) -> BTAbstimmung:
        bt_einzelabstimmungen = []
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
        bt_abstimmung_redner = []

        for redner in data.redner:
            bt_abstimmung_redner.append(
                BTAbstimmungRedner(
                    function=redner.function,
                    bt_video_id=redner.video_id,
                    video_url=redner.video_url.unicode_string(),
                    image_url=redner.image_url.unicode_string(),
                )
            )

        bt_abstimmung_drucksachen = []
        for drucksache in data.drucksachen:
            bt_abstimmung_drucksachen.append(
                BTAbstimmungDrucksache(
                    drucksache_url=drucksache.url.unicode_string(),
                    drucksache_name=drucksache.drucksache_name,
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
        )

        return bt_abstimmung

    def fetch_data(
        self,
        params: BundestagAbstimmungenPointerParameter | None = None,
        response_limit: int = 1000,
        proxy_list: ProxyList | None = None,
    ) -> Iterator[BTAbstimmung]:
        for abstimmung_pointer in self.facade.get_bundestag_abstimmung_pointers(
            params=params, response_limit=response_limit
        ):
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

            yield self.transform_model(bt_abstimmung)


def import_bt_abstimmungen():
    importer = BTAbstimmungenImporter()

    params = BundestagAbstimmungenPointerParameter(
        date_start=date(2021, 1, 1), date_end=date(2023, 12, 31)
    )

    importer.import_data(params=params, response_limit=1000, upsert_batch_size=1)


if __name__ == '__main__':
    configure_logging()
    import_bt_abstimmungen()
