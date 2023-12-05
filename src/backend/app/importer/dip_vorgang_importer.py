"""Class for DIP Bundestag Vorgang Importer."""

from typing import Iterator

from backend.app.core.config import Settings
from backend.app.crud.CRUDDIPBundestag.crud_vorgang import CRUD_DIP_VORGANG
from backend.app.facades.deutscher_bundestag.model import Vorgang
from backend.app.facades.deutscher_bundestag.parameter_model import VorgangParameter
from backend.app.facades.util import ProxyList
from backend.app.importer.dip_importer import DIPImporter

# import from all models to ensure they are registered
from backend.app.models.deutscher_bundestag.models import (
    DIPInkrafttreten,
    DIPVerkuendung,
    DIPVorgang,
    DIPVorgangDeskriptor,
    DIPVorgangVerlinkung,
)

import pytz
from datetime import datetime


class DIPBundestagVorgangImporter(DIPImporter[Vorgang, VorgangParameter, DIPVorgang]):
    """Class for DIP Bundestag Vorgang Importer."""

    def __init__(self):
        """
        Initialize DIPImporter.
        """
        super().__init__(CRUD_DIP_VORGANG)

    def transform_model(self, data: Vorgang) -> DIPVorgang:
        """Transform data."""

        dip_inkrafttreten = (
            [DIPInkrafttreten(**inkrafttreten.model_dump()) for inkrafttreten in data.inkrafttreten]
            if data.inkrafttreten
            else []
        )

        dip_verkuendung = (
            [DIPVerkuendung(**verkuendung.model_dump()) for verkuendung in data.verkuendung]
            if data.verkuendung
            else []
        )

        dip_vorgang_deskriptor = (
            [
                DIPVorgangDeskriptor(**vorgang_deskriptor.model_dump())
                for vorgang_deskriptor in data.deskriptor
            ]
            if data.deskriptor
            else []
        )

        dip_vorgang_verlinkung = (
            [
                DIPVorgangVerlinkung(**vorgang_verlinkung.model_dump())
                for vorgang_verlinkung in data.vorgang_verlinkung
            ]
            if data.vorgang_verlinkung
            else []
        )

        return DIPVorgang(
            **data.model_dump(
                exclude={
                    'inkrafttreten',
                    'verkuendung',
                    'deskriptor',
                    'vorgang_verlinkung',
                }
            ),
            inkrafttreten=dip_inkrafttreten,
            verkuendung=dip_verkuendung,
            deskriptor=dip_vorgang_deskriptor,
            vorgang_verlinkung=dip_vorgang_verlinkung,
        )

    def fetch_data(
        self,
        params: VorgangParameter | None = None,
        response_limit=1000,
        proxy_list: ProxyList | None = None,
    ) -> Iterator[Vorgang]:
        """Fetch data."""
        return self.dip_bundestag_facade.get_vorgange(
            params=params,
            response_limit=response_limit,
            proxy_list=proxy_list,
        )


def import_dip_bundestag():
    importer = DIPBundestagVorgangImporter()

    params = VorgangParameter(
        aktualisiert_start=datetime(2022, 1, 1, tzinfo=pytz.UTC).astimezone(),
    )

    importer.import_data(
        params=params,
        response_limit=10000,
    )


if __name__ == '__main__':
    import_dip_bundestag()
