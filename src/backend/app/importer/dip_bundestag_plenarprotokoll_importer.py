"""Class for DIP Bundestag Plenarprotokoll Importer."""

import logging

from backend.app.core.config import Settings
from backend.app.crud.CRUDDIPBundestag.crud_plenarprotokoll_vorgangsbezug import (
    CRUD_DIP_Plenarprotokoll_VORGANGSBEZUG,
)
from backend.app.facades.deutscher_bundestag.facade import DIPBundestagFacade
from backend.app.facades.deutscher_bundestag.model import Plenarprotokoll
from backend.app.facades.deutscher_bundestag.model_plenarprotokoll_vorgangsbezug import (
    PlenarprotokollVorgangsbezug,
)
from backend.app.models.deutscher_bundestag.plenarprotokoll_model import (
    DIPPlenarprotokollVorgangsbezug,
)

_logger = logging.getLogger(__name__)


class DIPBundestagPlenarprotokollImporter:
    def __init__(self) -> None:
        self.dip_bundestag_facade = DIPBundestagFacade.get_instance(Settings())
        self.plenarprotkolle: list[Plenarprotokoll] = []

    def import_plenarprotokolle(self, wahlperiode: int = 20):
        """Import plenarprotokolle."""
        self.plenarprotokolle = self.dip_bundestag_facade.get_plenarprotokolle(
            wahlperiode=wahlperiode
        )

        # TODO
        # insert into database (but for now we don't need them necessarily only vorgangsbezuge of plenarprotokolle)

    def import_plenarprotokoll_vrogangsbezuege(self, wahlperiode: int = 20):
        """Import plenarprokotll vorgangsbezuege."""

        if len(self.plenarprotkolle) == 0:
            self.import_plenarprotokolle(wahlperiode=wahlperiode)

        # fetch plenarprotokoll_vorgangsbezuege
        for plenarprotokoll in self.plenarprotkolle:
            _logger.info("Fetch vorgangsbezuge for plenarprotokoll with id %d", plenarprotokoll.id)
            plenarprotokoll_vorgangsbezuege: list[PlenarprotokollVorgangsbezug] = []
            plenarprotokoll_vorgangsbezuege.extend(
                self.dip_bundestag_facade.get_vorgangsbezuege_of_plenarprotokoll_by_id(
                    plenarprotokoll_id=plenarprotokoll.id
                )
            )

            # create record in database (add to database)
            _logger.info(
                "Add vorgangsbezuge for plenarprotokoll with id %d to database.", plenarprotokoll.id
            )
            CRUD_DIP_Plenarprotokoll_VORGANGSBEZUG.create_or_update_multi(
                DIPPlenarprotokollVorgangsbezug(plenarprotokoll_vorgangsbezuege)
            )
