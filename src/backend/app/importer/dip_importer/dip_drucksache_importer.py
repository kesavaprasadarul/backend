"""Class for DIP Bundestag Drucksache Importer."""

import time
from datetime import datetime
from logging import getLogger
from tokenize import endpats
from typing import Any, Iterator, Optional

import pytz

from backend.app.core.config import Settings
from backend.app.core.logging import configure_logging
from backend.app.crud.CRUDDIPBundestag.crud_drucksache import CRUD_DIP_DRUCKSACHE
from backend.app.facades.deutscher_bundestag.model import Drucksache, Vorgang, Zuordnung
from backend.app.facades.deutscher_bundestag.parameter_model import (
    DrucksacheParameter,
    VorgangParameter,
)
from backend.app.facades.util import ProxyList
from backend.app.importer.dip_importer.dip_importer import DIPImporter
from backend.app.importer.dip_importer.dip_vorgang_importer import DIPBundestagVorgangImporter

# import from all models to ensure they are registered
from backend.app.models.dip.models import (
    DIPAutor,
    DIPDrucksache,
    DIPFundstelle,
    DIPRessort,
    DIPUrheber,
    DIPVorgang,
    DIPVorgangsbezug,
)


class DIPBundestagDrucksacheImporter(DIPImporter[Drucksache, DrucksacheParameter, DIPDrucksache]):
    """Class for DIP Bundestag Drucksache Importer."""

    def __init__(
        self,
        import_vorgaenge: bool = True,
        import_vorgangspositionen: bool = True,
        raise_on_error: bool = False,
    ):
        """
        Initialize DIPImporter.
        """
        super().__init__(CRUD_DIP_DRUCKSACHE)

        self.import_vorgaenge = import_vorgaenge
        self.raise_on_error = raise_on_error
        if import_vorgaenge:
            self.vorgang_importer = DIPBundestagVorgangImporter(
                import_vorgangspositionen=import_vorgangspositionen, raise_on_error=raise_on_error
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
        )

    def fetch_count(
        self,
        params: Optional[DrucksacheParameter] = None,
        proxy_list: ProxyList | None = None,
    ) -> int:
        """Fetch count."""
        time.sleep(self.delay_between_requests)
        return self.facade.get_count(
            endpoint='/api/v1/drucksache',
            params=params,
            proxy_list=proxy_list,
        )

    def fetch_data(
        self,
        params: Optional[DrucksacheParameter] = None,
        response_limit=1000,
        proxy_list: ProxyList | None = None,
        **kwargs: Any,
    ) -> Iterator[DIPDrucksache]:
        """Fetch data."""

        for model in self.facade.get_drucksachen(
            params=params,
            response_limit=response_limit,
            proxy_list=proxy_list,
            raise_on_error=self.raise_on_error,
        ):
            # if model.id == 271560:
            #     print('debug')
            db_model = self.transform_model(model)

            if self.import_vorgaenge:
                time.sleep(self.delay_between_requests)
                for vorgang_pydantic in self.vorgang_importer.fetch_data(
                    params=VorgangParameter(
                        drucksache=db_model.id,
                    ),
                    proxy_list=proxy_list,
                ):
                    db_model.vorgaenge.append(vorgang_pydantic)

            yield db_model


def import_dip_bundestag():
    importer = DIPBundestagDrucksacheImporter(
        import_vorgaenge=True, import_vorgangspositionen=False
    )

    params = DrucksacheParameter(
        aktualisiert_start=datetime(2015, 1, 1, tzinfo=pytz.UTC).astimezone(),
        aktualisiert_end=datetime(2024, 1, 31, tzinfo=pytz.UTC).astimezone(),
    )

    importer.import_data(params=params, upsert_batch_size=30)


if __name__ == '__main__':
    configure_logging()
    import_dip_bundestag()
