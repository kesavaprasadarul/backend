"""Class for DIP Bundestag Drucksache Importer."""

from logging import getLogger
from typing import Iterator, Optional

from backend.app.core.config import Settings
from backend.app.crud.CRUDDIPBundestag.crud_drucksache import CRUD_DIP_DRUCKSACHE
from backend.app.facades.deutscher_bundestag.model import Drucksache, Vorgang, Zuordnung
from backend.app.facades.deutscher_bundestag.parameter_model import (
    DrucksacheParameter,
    VorgangParameter,
)
from backend.app.facades.util import ProxyList
from backend.app.importer.dip_importer import DIPImporter
from backend.app.importer.dip_vorgang_importer import DIPBundestagVorgangImporter

import pytz

from datetime import datetime

# import from all models to ensure they are registered
from backend.app.models.deutscher_bundestag.models import (
    DIPAutor,
    DIPDrucksache,
    DIPFundstelle,
    DIPRessort,
    DIPUrheber,
    DIPVorgang,
    DIPVorgangsbezug,
)

_logger = getLogger(__name__)


class DIPBundestagDrucksacheImporter(DIPImporter[Drucksache, DrucksacheParameter, DIPDrucksache]):
    """Class for DIP Bundestag Drucksache Importer."""

    def __init__(self, import_vorgaenge: bool = True):
        """
        Initialize DIPImporter.
        """
        super().__init__(CRUD_DIP_DRUCKSACHE)

        self.import_vorgaenge = import_vorgaenge
        if import_vorgaenge:
            self.vorgang_importer = DIPBundestagVorgangImporter()

    def transform_model(self, data: Drucksache) -> DIPDrucksache:
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

        return DIPDrucksache(
            **data.model_dump(
                exclude={
                    'autoren_anzeige',
                    'urheber',
                    'fundstelle',
                    'vorgangsbezug',
                    'ressort',
                }
            ),
            autoren=dip_autoren,
            fundstelle=dip_fundstelle,
            urheber=dip_urheber,
            vorgangsbezug=dip_vorgangsbezug,
            ressort=dip_ressort,
            vorgang=[],
        )

    def fetch_data(
        self,
        params: Optional[DrucksacheParameter] = None,
        response_limit=1000,
        proxy_list: ProxyList | None = None,
    ) -> Iterator[Drucksache]:
        """Fetch data."""

        return self.dip_bundestag_facade.get_drucksachen(
            params=params,
            response_limit=response_limit,
            proxy_list=proxy_list,
        )

    # def batch_upsert(
    #     self,
    #     params: Optional[DrucksacheParameter] = None,
    #     response_limit: int = 1000,
    #     proxy_list: ProxyList | None = None,
    #     upsert_batch_size: int = 100,
    #     **kwargs,
    # ):
    #     batch: list[DIPDrucksache] = []
    #     batch_count = 1
    #     for pydantic_model in self.fetch_data(
    #         params=params,
    #         response_limit=response_limit,
    #         proxy_list=proxy_list,
    #     ):
    #         _logger.info(f'Adding model {pydantic_model} to batch.')
    #         sql_model = self.transform_model(pydantic_model)

    #         if self.import_vorgaenge:
    #             for vorgang_pydantic in self.vorgang_importer.fetch_data(
    #                 params=VorgangParameter(
    #                     drucksache=sql_model.id,
    #                 ),
    #                 proxy_list=proxy_list,
    #             ):
    #                 sql_model.vorgang.append(
    #                     self.vorgang_importer.transform_model(vorgang_pydantic)
    #                 )

    #         batch.append(sql_model)

    #         if len(batch) >= upsert_batch_size:
    #             _logger.info(f'Upserting batch {batch_count} into {sql_model.__tablename__}-Table.')
    #             self.crud.create_or_update_multi(batch)
    #             batch = []
    #             batch_count += 1

    #     if batch:
    #         _logger.info(
    #             f'Upserting final batch ({batch_count}) into {batch[0].__tablename__}-Table.'
    #         )
    #         self.crud.create_or_update_multi(batch)

    def import_data(
        self,
        params: Optional[DrucksacheParameter] = None,
        response_limit: int = 1000,
        proxy_list: ProxyList | None = None,
        upsert_batch_size: int = 100,
        **kwargs,
    ):
        """Import data."""

        self.batch_upsert(
            params=params,
            response_limit=response_limit,
            proxy_list=proxy_list,
            upsert_batch_size=upsert_batch_size,
            **kwargs,
        )


def import_dip_bundestag():
    importer = DIPBundestagDrucksacheImporter()

    params = DrucksacheParameter(
        aktualisiert_start=datetime(2022, 1, 1, tzinfo=pytz.UTC).astimezone(),
    )

    importer.import_data(
        params=params,
        response_limit=10000,
    )


if __name__ == '__main__':
    import_dip_bundestag()
