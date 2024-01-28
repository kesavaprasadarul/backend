"""CRUD Operations Bundestag Abstimmung Redner."""
import datetime
import logging

from backend.app.crud.base import CRUDBase
from backend.app.models.bundestag.abstimmung_model import BTAbstimmungRedner

_logger = logging.getLogger(__name__)


class CRUDBundestagAbstimmungRedner(CRUDBase[BTAbstimmungRedner]):
    """Provides CRUD operations for bt.abstimmung_redner table."""

    def __init__(self, model: type):
        """
        Initialize CRUDDIPDrucksache.
        """
        super().__init__(model)


CRUD_BUNDESTAG_ABSTIMMUNG_REDNER = CRUDBundestagAbstimmungRedner(BTAbstimmungRedner)
