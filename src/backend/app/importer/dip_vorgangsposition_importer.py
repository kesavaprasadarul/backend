"""Class for DIP Bundestag Vorgangsposition Importer."""

from backend.app.core.config import Settings
from backend.app.crud.CRUDDIPBundestag.crud_vorgangsposition import CRUD_DIP_VORGANGSPOSITION
from backend.app.facades.deutscher_bundestag.model import Vorgangsposition
from backend.app.importer.dip_importer import DIPImporter
from backend.app.facades.util import ProxyList

# import from all models to ensure they are registered
from backend.app.models.deutscher_bundestag.models import (
    DIPVorgangsposition,
    DIPAktivitaetAnzeige,
    DIPUeberweisung,
    DIPBeschlussfassung,
    DIPFundstelle,
    DIPUrheber,
    DIPRessort,
    DIPVorgangspositionbezug,
)


from typing import Iterator


class DIPBundestagVorgangspositionImporter(DIPImporter[Vorgangsposition, DIPVorgangsposition]):
    """Class for DIP Bundestag Vorgangsposition Importer."""

    def __init__(self):
        """
        Initialize DIPImporter.
        """
        super().__init__(CRUD_DIP_VORGANGSPOSITION)

    def transform_model(self, data: Vorgangsposition) -> DIPVorgangsposition:
        """Transform data."""

        dip_aktivitaet_anzeige = (
            [
                DIPAktivitaetAnzeige(**aktivitaet_anzeige.model_dump())
                for aktivitaet_anzeige in data.aktivitaet_anzeige
            ]
            if data.aktivitaet_anzeige
            else []
        )

        dip_vorgangspositionbezug = (
            [
                DIPVorgangspositionbezug(
                    **vorgangspositionbezug.model_dump(
                        exclude={'id'},
                    ),
                    from_vorgang_id=data.vorgang_id,
                    to_vorgang_id=vorgangspositionbezug.id,
                )
                for vorgangspositionbezug in data.mitberaten
            ]
            if data.mitberaten
            else []
        )

        dip_ueberweisung = (
            [DIPUeberweisung(**ueberweisung.model_dump()) for ueberweisung in data.ueberweisung]
            if data.ueberweisung
            else []
        )

        dip_beschlussfassung = (
            [
                DIPBeschlussfassung(**beschlussfassung.model_dump())
                for beschlussfassung in data.beschlussfassung
            ]
            if data.beschlussfassung
            else []
        )

        dip_fundstelle = (
            DIPFundstelle(**data.fundstelle.model_dump(exclude={'fk_id'}))
            if data.fundstelle
            else None
        )

        dip_urheber = (
            [DIPUrheber(**urheber.model_dump()) for urheber in data.urheber] if data.urheber else []
        )

        dip_ressort = (
            [DIPRessort(**ressort.model_dump()) for ressort in data.ressort] if data.ressort else []
        )

        return DIPVorgangsposition(
            **data.model_dump(
                exclude={
                    'aktivitaet_anzeige',
                    'ueberweisung',
                    'beschlussfassung',
                    'fundstelle',
                    'urheber',
                    'ressort',
                    'mitberaten',
                }
            ),
            aktivitaet_anzeige=dip_aktivitaet_anzeige,
            ueberweisung=dip_ueberweisung,
            beschlussfassung=dip_beschlussfassung,
            fundstelle=dip_fundstelle,
            urheber=dip_urheber,
            ressort=dip_ressort,
            vorgangspositionbezug=dip_vorgangspositionbezug,
        )

    def fetch_data(
        self,
        params: dict,
        response_limit=1000,
        proxy_list: ProxyList | None = None,
        *args,
        **kwargs,
    ) -> Iterator[Vorgangsposition]:
        """Fetch data."""

        since_datetime = params.get("since_datetime", '2021-01-01T00:00:00.000Z')

        return self.dip_bundestag_facade.get_vorgangspositionen(
            since_datetime=since_datetime,
            response_limit=response_limit,
            proxy_list=proxy_list,
            *args,
            **kwargs,
        )


def import_dip_bundestag():
    importer = DIPBundestagVorgangspositionImporter()

    importer.import_data(
        params={
            "since_datetime": '2021-01-01T00:00:00.000Z',
        },
        response_limit=1,
        proxy_list=ProxyList.from_url(Settings().PROXY_LIST_URL),
    )


if __name__ == '__main__':
    import_dip_bundestag()
