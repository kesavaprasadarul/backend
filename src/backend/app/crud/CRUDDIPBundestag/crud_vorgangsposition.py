"""CRUD Operations DIP Bundestag for Vorgangsposition."""
import logging

from backend.app.crud.base import CRUDBase
from backend.app.models.deutscher_bundestag.vorgangsposition_model import DIPVorgangsposition

_logger = logging.getLogger(__name__)


class CRUDDIPVorgangsposition(CRUDBase[DIPVorgangsposition]):
    """Provides CRUD operations for dip.vorgangsposition table."""

    def __init__(self, model: type):
        """
        Initialize CRUDDIPVorgangsposition.
        """
        super().__init__(model)


CRUD_DIP_VORGANGSPOSITION = CRUDDIPVorgangsposition(DIPVorgangsposition)
