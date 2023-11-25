"""CRUD Operations DIP Bundestag for Drucksache."""
import logging

from backend.app.crud.base import CRUDBase
from backend.app.models.deutscher_bundestag.drucksache_model import DIPDrucksache

_logger = logging.getLogger(__name__)


class CRUDDIPDrucksache(CRUDBase[DIPDrucksache]):
    """Provides CRUD operations for dip.drucksache table."""

    def __init__(self, model: type):
        """
        Initialize CRUDDIPDrucksache.
        """
        super().__init__(model)


CRUD_DIP_DRUCKSACHE = CRUDDIPDrucksache(DIPDrucksache)
