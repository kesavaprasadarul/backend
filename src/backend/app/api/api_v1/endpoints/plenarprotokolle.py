"""Contains endpoints for importing PLENARPROTOKOLLE from DIP Bundestag API with DIP Bundestag facade."""
import logging

import fastapi

from backend.app.importer.dip_plenarprotokoll_importer import DIPBundestagPlenarprotokollImporter

_logger = logging.getLogger(__name__)

router = fastapi.APIRouter()


@router.post(
    "/plenarprotkolle",
    tags=["plenarprotokoll"],
)
def import_plenarprotkolle():
    DIPBundestagPlenarprotokollImporter().import_data()
