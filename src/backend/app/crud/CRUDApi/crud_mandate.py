"""CRUD Operations DIP Bundestag for Drucksache."""
import logging

import sqlalchemy as sa
from pydantic import BaseModel

from backend.app.crud.base import CRUDBase
from backend.app.models.api.mandate_model import APIMandate

_logger = logging.getLogger(__name__)


class CRUDMandate(CRUDBase[APIMandate]):
    """Provides CRUD operations for public.mandate table."""

    def __init__(self, model: type):
        """
        Initialize CRUDDIPDrucksache.
        """
        super().__init__(model)


CRUD_Mandate = CRUDMandate(APIMandate)
