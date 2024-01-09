"""CRUD Operations DIP Bundestag for Drucksache."""
import logging
from datetime import date, datetime

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

    def read_wahlperiode_by_date(self, date: date) -> int:
        """
        Read Wahlperiode by date.
        """
        _logger.info("Read Wahlperiode by date")

        if date < datetime.strptime("1949-09-07", "%Y-%m-%d").date():
            raise ValueError("Date must be after 1949-09-07")

        query = sa.select(self.model.wahlperiode).where(
            sa.and_(
                self.model.date_from <= date,
                sa.or_(self.model.date_to >= date, self.model.date_to == None),
            )
        )
        result = self.db.execute(query)
        return result.scalar_one()


CRUD_MANDATE = CRUDMandate(APIMandate)
