"""Class for DIP Bundestag Plenarprotokoll Importer."""

from typing import Iterator

from backend.app.core.config import Settings
from backend.app.crud.CRUDDIPBundestag.crud_plenarprotokoll import CRUD_DIP_PLENARPROTOKOLL
from backend.app.facades.deutscher_bundestag.model import PlenarprotokollText
from backend.app.facades.deutscher_bundestag.parameter_model import PlenarprotokollParameter
from backend.app.facades.util import ProxyList
from backend.app.importer.dip_importer import DIPImporter

# import from all models to ensure they are registered
from backend.app.models.deutscher_bundestag.models import (
    DIPFundstelle,
    DIPPlenarprotokoll,
    DIPPlenarprotokollText,
    DIPVorgangsbezug,
)


class DIPBundestagPlenarprotokollImporter(
    DIPImporter[PlenarprotokollText, PlenarprotokollParameter, DIPPlenarprotokoll]
):
    """Class for DIP Bundestag Plenarprotokoll Importer."""

    def __init__(self):
        """
        Initialize DIPImporter.
        """
        super().__init__(CRUD_DIP_PLENARPROTOKOLL)

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
    ) -> Iterator[PlenarprotokollText]:
        """Fetch data."""

        return self.dip_bundestag_facade.get_plenarprotokolle_text(
            params=params,
            response_limit=response_limit,
            proxy_list=proxy_list,
        )


def import_dip_bundestag():
    importer = DIPBundestagPlenarprotokollImporter()

    importer.import_data(
        params=None,
        response_limit=1,
        proxy_list=ProxyList.from_url(Settings().PROXY_LIST_URL),
    )


if __name__ == '__main__':
    import_dip_bundestag()
