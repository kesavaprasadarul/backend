"""Class for DIP Bundestag Plenarprotokoll Importer."""

from backend.app.core.config import Settings
from backend.app.crud.CRUDDIPBundestag.crud_plenarprotokoll import (
    CRUD_DIP_PLENARPROTOKOLL,
)
from backend.app.facades.deutscher_bundestag.model import Plenarprotokoll
from backend.app.importer.dip_importer import DIPImporter
from backend.app.facades.util import ProxyList

# import from all models to ensure they are registered
from backend.app.models.deutscher_bundestag.models import (
    DIPPlenarprotokoll,
    DIPFundstelle,
    DIPVorgangsbezug,
)


from typing import Iterator


class DIPBundestagPlenarprotokollImporter(DIPImporter[Plenarprotokoll, DIPPlenarprotokoll]):
    """Class for DIP Bundestag Plenarprotokoll Importer."""

    def __init__(self):
        """
        Initialize DIPImporter.
        """
        super().__init__(CRUD_DIP_PLENARPROTOKOLL)

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
        params: dict,
        response_limit=1000,
        proxy_list: ProxyList | None = None,
        *args,
        **kwargs,
    ) -> Iterator[Plenarprotokoll]:
        """Fetch data."""

        wahlperiode = params.get("wahlperiode", 20)
        zuordnung = params.get("zuordnung", "BT")

        return self.dip_bundestag_facade.get_plenarprotokolle(
            wahlperiode=wahlperiode,
            zuordnung=zuordnung,
            response_limit=response_limit,
            proxy_list=proxy_list,
            *args,
            **kwargs,
        )


def import_dip_bundestag():
    importer = DIPBundestagPlenarprotokollImporter()

    importer.import_data(
        params={
            "wahlperiode": 20,
            "zuordnung": "BT",
        },
        response_limit=1,
        proxy_list=ProxyList.from_url(Settings().PROXY_LIST_URL),
    )


if __name__ == '__main__':
    import_dip_bundestag()
