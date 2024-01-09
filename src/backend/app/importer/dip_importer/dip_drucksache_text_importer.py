"""Class for DIP Bundestag Drucksache-Text Importer."""

import time
from datetime import date, datetime, timezone
from typing import Any, Iterator, Optional

from backend.app.core.config import Settings
from backend.app.core.logging import configure_logging
from backend.app.crud.CRUDDIPBundestag.crud_drucksache import CRUD_DIP_DRUCKSACHE
from backend.app.facades.deutscher_bundestag.model import DrucksacheText
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
    DIPDrucksacheText,
    DIPFundstelle,
    DIPRessort,
    DIPUrheber,
    DIPVorgangsbezug,
)


class DIPBundestagDrucksacheTextImporter(
    DIPImporter[DrucksacheText, DrucksacheParameter, DIPDrucksache]
):
    """Class for DIP Bundestag Drucksache-Text Importer."""

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

    def transform_model(self, data: DrucksacheText) -> DIPDrucksache:
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

        dip_drucksache_text = (
            DIPDrucksacheText(
                drucksache_id=data.id,
                text=data.text,
            )
            if data.text
            else None
        )

        return DIPDrucksache(
            **data.model_dump(
                exclude={
                    'autoren_anzeige',
                    'urheber',
                    'fundstelle',
                    'vorgangsbezug',
                    'ressort',
                    'text',
                }
            ),
            autoren=dip_autoren,
            fundstelle=dip_fundstelle,
            urheber=dip_urheber,
            vorgangsbezug=dip_vorgangsbezug,
            ressort=dip_ressort,
            drucksache_text=dip_drucksache_text,
        )

    def fetch_data(
        self,
        params: Optional[DrucksacheParameter] = None,
        response_limit=1000,
        proxy_list: ProxyList | None = None,
        **kwargs: Any,
    ) -> Iterator[DIPDrucksache]:
        """Fetch data."""

        for model in self.facade.get_drucksachen_text(
            params=params,
            response_limit=response_limit,
            proxy_list=proxy_list,
        ):
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
    importer = DIPBundestagDrucksacheTextImporter()

    params = DrucksacheParameter(
        aktualisiert_start=datetime(2021, 1, 1, tzinfo=timezone.utc).astimezone(),
    )

    importer.import_data(
        params=params,
        response_limit=1,
        proxy_list=ProxyList.from_url(Settings().PROXY_LIST_SOCKS4_URL),
    )


if __name__ == '__main__':
    configure_logging()
    import_dip_bundestag()
