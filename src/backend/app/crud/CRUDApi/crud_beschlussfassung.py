"""CRUD Operations DIP Bundestag for Drucksache."""
import logging

import sqlalchemy as sa
from pydantic import BaseModel

from backend.app.crud.base import CRUDBase
from backend.app.models.api.beschlussfassung_model import APIBeschlussfassung

_logger = logging.getLogger(__name__)


class CRUDBeschlussfassung(CRUDBase[APIBeschlussfassung]):
    """Provides CRUD operations for public.beschlussfassung table."""

    def __init__(self, model: type):
        """
        Initialize CRUDDIPDrucksache.
        """
        super().__init__(model)

    def update_beschlussfassung(
        self, drucksachetyp_filter: list[str] | None, vorgangstyp_filter: list[str] | None
    ) -> None:
        """Call import procedure."""
        _logger.info("Call import procedure for %s", self.model.__tablename__)
        CRUDBase.db.execute(
            sa.text("CALL public.import_beschlussfassung(:drucksachetyp, :vorgangstyp)"),
            {"drucksachetyp": drucksachetyp_filter, "vorgangstyp": vorgangstyp_filter},
        )


CRUD_Beschlussfassung = CRUDBeschlussfassung(APIBeschlussfassung)
