"""Class for DIP Bundestag Drucksache-Text Importer."""

from typing import Iterator

from backend.app.core.config import Settings
from backend.app.crud.CRUDDIPBundestag.crud_drucksache import CRUD_DIP_DRUCKSACHE
from backend.app.facades.deutscher_bundestag.model import DrucksacheText
from backend.app.facades.util import ProxyList
from backend.app.importer.dip_importer import DIPImporter

# import from all models to ensure they are registered
from backend.app.models.deutscher_bundestag.models import (
    DIPAutor,
    DIPDrucksache,
    DIPDrucksacheText,
    DIPFundstelle,
    DIPRessort,
    DIPUrheber,
    DIPVorgangsbezug,
)


class DIPBundestagDrucksacheTextImporter(DIPImporter[DrucksacheText, DIPDrucksache]):
    """Class for DIP Bundestag Drucksache-Text Importer."""

    def __init__(self):
        """
        Initialize DIPImporter.
        """
        super().__init__(CRUD_DIP_DRUCKSACHE)

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
        params: dict,
        response_limit=1000,
        proxy_list: ProxyList | None = None,
        *args,
        **kwargs,
    ) -> Iterator[DrucksacheText]:
        """Fetch data."""

        since_datetime = params.get("since_datetime", '2021-01-01T00:00:00.000Z')

        return self.dip_bundestag_facade.get_drucksachen_text(
            since_datetime=since_datetime,
            response_limit=response_limit,
            proxy_list=proxy_list,
            *args,
            **kwargs,
        )


def import_dip_bundestag():
    importer = DIPBundestagDrucksacheTextImporter()

    importer.import_data(
        params={
            "since_datetime": '2021-01-01T00:00:00.000Z',
        },
        response_limit=1,
        proxy_list=ProxyList.from_url(Settings().PROXY_LIST_URL),
    )


if __name__ == '__main__':
    import_dip_bundestag()
