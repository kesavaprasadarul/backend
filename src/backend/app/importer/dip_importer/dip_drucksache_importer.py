"""Class for DIP Bundestag Drucksache Importer."""

import time
from datetime import datetime
from logging import getLogger
from typing import Iterator, Optional

import pytz

from backend.app.core.config import Settings
from backend.app.crud.CRUDDIPBundestag.crud_drucksache import CRUD_DIP_DRUCKSACHE
from backend.app.facades.deutscher_bundestag.model import Drucksache, Vorgang, Zuordnung
from backend.app.facades.deutscher_bundestag.parameter_model import (
    DrucksacheParameter,
    VorgangParameter,
)
from backend.app.facades.util import ProxyList
from backend.app.importer.dip_importer.base import DIPImporter
from backend.app.importer.dip_importer.dip_vorgang_importer import DIPBundestagVorgangImporter

# import from all models to ensure they are registered
from backend.app.models.deutscher_bundestag.models import (
    DIPAutor,
    DIPDrucksache,
    DIPFundstelle,
    DIPRessort,
    DIPUrheber,
    DIPVorgang,
    DIPVorgangsbezug,
)
from backend.app.core.logging import configure_logging

_logger = getLogger(__name__)


class DIPBundestagDrucksacheImporter(DIPImporter[Drucksache, DrucksacheParameter, DIPDrucksache]):
    """Class for DIP Bundestag Drucksache Importer."""

    def __init__(self, import_vorgaenge: bool = True, import_vorgangspositionen: bool = True):
        """
        Initialize DIPImporter.
        """
        super().__init__(CRUD_DIP_DRUCKSACHE)

        self.import_vorgaenge = import_vorgaenge
        if import_vorgaenge:
            self.vorgang_importer = DIPBundestagVorgangImporter(
                import_vorgangspositionen=import_vorgangspositionen
            )

    def transform_model(self, data: Drucksache) -> DIPDrucksache:
        """Transform data."""

        dip_autoren = (
            [DIPAutor(**autor.model_dump()) for autor in data.autoren_anzeige]
            if data.autoren_anzeige
            else []
        )

        dip_fundstelle = DIPFundstelle(**data.fundstelle.model_dump(exclude={'fk_id'}))

        dip_urheber = (
            [DIPUrheber(**urheber.model_dump()) for urheber in data.urheber] if data.urheber else []
        )

        dip_vorgangsbezug = (
            [
                DIPVorgangsbezug(
                    **vorgangsbezug.model_dump(exclude={'id'}), vorgang_id=vorgangsbezug.id
                )
                for vorgangsbezug in data.vorgangsbezug
            ]
            if data.vorgangsbezug
            else []
        )

        dip_ressort = (
            [DIPRessort(**ressort.model_dump()) for ressort in data.ressort] if data.ressort else []
        )

        return DIPDrucksache(
            **data.model_dump(
                exclude={
                    'autoren_anzeige',
                    'urheber',
                    'fundstelle',
                    'vorgangsbezug',
                    'ressort',
                }
            ),
            autoren=dip_autoren,
            fundstelle=dip_fundstelle,
            urheber=dip_urheber,
            vorgangsbezug=dip_vorgangsbezug,
            ressort=dip_ressort,
            vorgang=[],
        )

    def fetch_data(
        self,
        params: Optional[DrucksacheParameter] = None,
        response_limit=1000,
        proxy_list: ProxyList | None = None,
    ) -> Iterator[DIPDrucksache]:
        """Fetch data."""

        for model in self.dip_bundestag_facade.get_drucksachen(
            params=params,
            response_limit=response_limit,
            proxy_list=proxy_list,
        ):
            db_model = self.transform_model(model)

            if self.import_vorgaenge:
                time.sleep(0.5)
                for vorgang_pydantic in self.vorgang_importer.fetch_data(
                    params=VorgangParameter(
                        drucksache=db_model.id,
                    ),
                    proxy_list=proxy_list,
                ):
                    db_model.vorgang.append(vorgang_pydantic)

            yield db_model


def import_dip_bundestag():
    importer = DIPBundestagDrucksacheImporter()

    params = DrucksacheParameter(
        aktualisiert_start=datetime(2022, 1, 1, tzinfo=pytz.UTC).astimezone(),
    )

    importer.import_data(
        params=params,
        response_limit=1,
    )


if __name__ == '__main__':
    import_dip_bundestag()
    configure_logging()
