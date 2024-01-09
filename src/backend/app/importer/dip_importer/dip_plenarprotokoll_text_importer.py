"""Class for DIP Bundestag Plenarprotokoll Importer."""

import datetime
import time
from typing import Any, Iterator

from backend.app.core.config import Settings
from backend.app.core.logging import configure_logging
from backend.app.crud.CRUDDIPBundestag.crud_plenarprotokoll import CRUD_DIP_PLENARPROTOKOLL
from backend.app.facades.deutscher_bundestag.model import PlenarprotokollText
from backend.app.facades.deutscher_bundestag.parameter_model import (
    PlenarprotokollParameter,
    VorgangParameter,
)
from backend.app.facades.util import ProxyList
from backend.app.importer.dip_importer.dip_importer import DIPImporter
from backend.app.importer.dip_importer.dip_vorgang_importer import DIPBundestagVorgangImporter

# import from all models to ensure they are registered
from backend.app.models.dip.models import (
    DIPFundstelle,
    DIPPlenarprotokoll,
    DIPPlenarprotokollText,
    DIPVorgangsbezug,
)


class DIPBundestagPlenarprotokollImporter(
    DIPImporter[PlenarprotokollText, PlenarprotokollParameter, DIPPlenarprotokoll]
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

    def transform_model(self, data: PlenarprotokollText) -> DIPPlenarprotokoll:
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

        dip_plenarprotokoll_text = (
            DIPPlenarprotokollText(plenarprotokoll_id=data.id, text=data.text)
            if data.text
            else None
        )

        return DIPPlenarprotokoll(
            **data.model_dump(exclude={'fundstelle', 'vorgangsbezug', 'text'}),
            fundstelle=dip_fundstelle,
            vorgangsbezug=dip_vorgangsbezug,
            plenarprotokoll_text=dip_plenarprotokoll_text,
        )

    def fetch_data(
        self,
        params: PlenarprotokollParameter | None = None,
        response_limit=1000,
        proxy_list: ProxyList | None = None,
        **kwargs: Any,
    ) -> Iterator[DIPPlenarprotokoll]:
        """Fetch data."""

        for model in self.facade.get_plenarprotokolle_text(params, response_limit, proxy_list):
            db_model = self.transform_model(model)

            if self.import_vorgaenge:
                time.sleep(self.delay_between_requests)
                for vorgang in self.vorgang_importer.fetch_data(
                    params=VorgangParameter(
                        plenarprotokoll=db_model.id,
                    ),
                    proxy_list=proxy_list,
                ):
                    db_model.vorgaenge.append(vorgang)

            yield db_model


def import_dip_bundestag():
    importer = DIPBundestagPlenarprotokollImporter()

    params = PlenarprotokollParameter(
        datum_start=datetime.date(2023, 1, 1), datum_end=datetime.date(2023, 12, 31)
    )

    importer.import_data(
        params=params,
        response_limit=100,
    )


if __name__ == '__main__':
    configure_logging()
    import_dip_bundestag()
