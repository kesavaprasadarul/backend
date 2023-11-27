"""Class for DIP Bundestag Vorgang Importer."""

from backend.app.core.config import Settings
from backend.app.crud.CRUDDIPBundestag.crud_vorgang import (
    CRUD_DIP_VORGANG,
)
from backend.app.facades.deutscher_bundestag.model import Vorgang
from backend.app.importer.dip_importer import DIPImporter
from backend.app.facades.util import ProxyList

# import from all models to ensure they are registered
from backend.app.models.deutscher_bundestag.models import (
    DIPVorgang,
    DIPInkrafttreten,
    DIPVerkuendung,
    DIPVorgangDeskriptor,
    DIPVorgangVerlinkung,
)


from typing import Iterator


class DIPBundestagVorgangImporter(DIPImporter[Vorgang, DIPVorgang]):
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
        params: dict,
        response_limit=1000,
        proxy_list: ProxyList | None = None,
        *args,
        **kwargs,
    ) -> Iterator[Vorgang]:
        """Fetch data."""

        since_datetime = params.get("since_datetime", '2021-01-01T00:00:00.000Z')

        return self.dip_bundestag_facade.get_vorgange(
            since_datetime=since_datetime,
            response_limit=response_limit,
            proxy_list=proxy_list,
            *args,
            **kwargs,
        )


def import_dip_bundestag():
    importer = DIPBundestagVorgangImporter()

    importer.import_data(
        params={
            "since_datetime": '2021-01-01T00:00:00.000Z',
        },
        response_limit=1,
        proxy_list=ProxyList.from_url(Settings().PROXY_LIST_URL),
    )


if __name__ == '__main__':
    import_dip_bundestag()
