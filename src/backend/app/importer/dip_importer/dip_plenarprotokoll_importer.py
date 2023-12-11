"""Class for DIP Bundestag Plenarprotokoll Importer."""

import time
from typing import Iterator

from backend.app.core.config import Settings
from backend.app.core.logging import configure_logging
from backend.app.crud.CRUDDIPBundestag.crud_plenarprotokoll import CRUD_DIP_PLENARPROTOKOLL
from backend.app.facades.deutscher_bundestag.model import Plenarprotokoll
from backend.app.facades.deutscher_bundestag.parameter_model import (
    PlenarprotokollParameter,
    VorgangParameter,
)
from backend.app.facades.util import ProxyList
from backend.app.importer.dip_importer.base import DIPImporter
from backend.app.importer.dip_importer.dip_vorgang_importer import DIPBundestagVorgangImporter

# import from all models to ensure they are registered
from backend.app.models.deutscher_bundestag.models import (
    DIPFundstelle,
    DIPPlenarprotokoll,
    DIPVorgang,
    DIPVorgangsbezug,
)


class DIPBundestagPlenarprotokollImporter(
    DIPImporter[Plenarprotokoll, PlenarprotokollParameter, DIPPlenarprotokoll]
):
    """Class for DIP Bundestag Plenarprotokoll Importer."""

    def __init__(self, import_vorgaenge: bool = True, import_vorgangspositionen: bool = True):
        """
        Initialize DIPImporter.
        """
        super().__init__(CRUD_DIP_PLENARPROTOKOLL)

        self.import_vorgaenge = import_vorgaenge
        self.import_vorgangspositionen = import_vorgangspositionen

        if import_vorgaenge:
            self.vorgang_importer = DIPBundestagVorgangImporter(
                import_vorgangspositionen=import_vorgangspositionen
            )

    def transform_model(self, data: Plenarprotokoll) -> DIPPlenarprotokoll:
        """Transform data."""

        dip_fundstelle = DIPFundstelle(**data.fundstelle.model_dump(exclude={"fk_id"}))

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

        return DIPPlenarprotokoll(
            **data.model_dump(exclude={'fundstelle', 'vorgangsbezug'}),
            fundstelle=dip_fundstelle,
            vorgangsbezug=dip_vorgangsbezug,
        )

    def fetch_data(
        self,
        params: PlenarprotokollParameter | None = None,
        response_limit=1000,
        proxy_list: ProxyList | None = None,
    ) -> Iterator[DIPPlenarprotokoll]:
        """Fetch data."""

        for model in self.dip_bundestag_facade.get_plenarprotokolle(
            params=params,
            response_limit=response_limit,
            proxy_list=proxy_list,
        ):
            db_model = self.transform_model(model)

            if self.import_vorgaenge:
                time.sleep(self.delay_between_requests)
                for vorgang in self.vorgang_importer.fetch_data(
                    params=VorgangParameter(
                        drucksache=db_model.id,
                    ),
                    proxy_list=proxy_list,
                ):
                    db_model.vorgang.append(vorgang)

            yield db_model


def import_dip_bundestag():
    importer = DIPBundestagPlenarprotokollImporter()

    params = PlenarprotokollParameter()

    importer.import_data(
        params=params,
        response_limit=1,
    )


if __name__ == '__main__':
    configure_logging()
    import_dip_bundestag()
