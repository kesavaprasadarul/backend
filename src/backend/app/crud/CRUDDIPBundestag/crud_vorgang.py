"""CRUD Operations DIP Bundestag for Vorgang."""
import logging

from backend.app.crud.base import CRUDBase
from backend.app.models.deutscher_bundestag.vorgang_model import DIPVorgang

_logger = logging.getLogger(__name__)


class CRUDDIPVorgang(CRUDBase[DIPVorgang]):
    """Provides CRUD operations for dip.vorgang table."""

    def __init__(self, model: type):
        """
        Initialize CRUDDIPVorgang.
        """
        super().__init__(model)


CRUD_DIP_VORGANG = CRUDDIPVorgang(DIPVorgang)
