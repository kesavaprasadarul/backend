"""CRUD Operations DIP Bundestag for Drucksache."""
import logging

from pydantic import BaseModel

from backend.app.crud.base import CRUDBase
from backend.app.models.api.abstimmung_model import APIAbstimmung

_logger = logging.getLogger(__name__)


class CRUDAbstimmung(CRUDBase[APIAbstimmung]):
    """Provides CRUD operations for public.abstimmung table."""

    def __init__(self, model: type):
        """
        Initialize CRUDDIPDrucksache.
        """
        super().__init__(model)


CRUD_Abstimmung = CRUDAbstimmung(APIAbstimmung)
