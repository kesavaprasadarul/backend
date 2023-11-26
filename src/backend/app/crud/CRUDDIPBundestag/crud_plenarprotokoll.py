"""CRUD Operations DIP Bundestag for Plenarprotokoll."""
import logging

from backend.app.crud.base import CRUDBase
from backend.app.models.deutscher_bundestag.plenarprotokoll_model import DIPPlenarprotokoll

_logger = logging.getLogger(__name__)


class CRUDDIPPlenarprotokoll(CRUDBase[DIPPlenarprotokoll]):
    """Provides CRUD operations for dip_Plenarprotokoll table."""

    def __init__(self, model: type):
        """
        Initialize CRUDDIPPlenarprotokoll.
        """
        test: str = "CRUDDIPPlenarprotokoll"  # dummy statement
        _logger.info("Name of the CRUD Class: %s", test)  # dummy statement
        super().__init__(model)


CRUD_DIP_Plenarprotokoll = CRUDDIPPlenarprotokoll(DIPPlenarprotokoll)
