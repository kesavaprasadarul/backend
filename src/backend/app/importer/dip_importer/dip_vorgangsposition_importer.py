"""Class for DIP Bundestag Vorgangsposition Importer."""

import logging
from datetime import datetime, date
from typing import Iterator

import pytz

from backend.app.core.config import Settings
from backend.app.core.logging import configure_logging
from backend.app.crud.CRUDDIPBundestag.crud_vorgangsposition import CRUD_DIP_VORGANGSPOSITION
from backend.app.facades.deutscher_bundestag.model import Vorgangsposition, Zuordnung
from backend.app.facades.deutscher_bundestag.parameter_model import VorgangspositionParameter
from backend.app.facades.util import ProxyList
from backend.app.importer.dip_importer.dip_importer import DIPImporter

# import from all models to ensure they are registered
from backend.app.models.dip.models import (
    DIPAktivitaetAnzeige,
    DIPBeschlussfassung,
    DIPFundstelle,
    DIPRessort,
    DIPUeberweisung,
    DIPUrheber,
    DIPVorgangsposition,
    DIPVorgangspositionbezug,
)


class DIPBundestagVorgangspositionImporter(
    DIPImporter[Vorgangsposition, VorgangspositionParameter, DIPVorgangsposition]
):
    """Class for DIP Bundestag Vorgangsposition Importer."""

    def __init__(self, raise_on_error: bool = False):
        """
        Initialize DIPImporter.
        """
        super().__init__(CRUD_DIP_VORGANGSPOSITION)

        self.raise_on_error = raise_on_error

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
        params: VorgangspositionParameter | None = None,
        response_limit=1000,
        proxy_list: ProxyList | None = None,
    ) -> Iterator[DIPVorgangsposition]:
        """Fetch data."""

        for model in self.facade.get_vorgangspositionen(
            params=params,
            response_limit=response_limit,
            proxy_list=proxy_list,
            raise_on_error=self.raise_on_error,
        ):
            db_model = self.transform_model(model)

            yield db_model


def import_dip_bundestag():
    importer = DIPBundestagVorgangspositionImporter()

    params = VorgangspositionParameter(datum_start=date(2023, 1, 1))
    importer.import_data(params=params, response_limit=10000)


if __name__ == '__main__':
    configure_logging()
    import_dip_bundestag()
