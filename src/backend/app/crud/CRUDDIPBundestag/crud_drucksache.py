"""CRUD Operations DIP Bundestag for Drucksache."""
import datetime
import logging

import pytz
import sqlalchemy as sa
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError

from backend.app.crud.base import CRUDBase
from backend.app.facades.deutscher_bundestag.model import Zuordnung
from backend.app.models.dip.drucksache_model import DIPDrucksache

_logger = logging.getLogger(__name__)


class CountsPerWeek(BaseModel):
    """Model for counts per week."""

    year: int
    week: int
    week_start_date: datetime.date
    week_end_date: datetime.date
    drucksache_count: int


class CRUDDIPDrucksache(CRUDBase[DIPDrucksache]):
    """Provides CRUD operations for dip.drucksache table."""

    def __init__(self, model: type):
        """
        Initialize CRUDDIPDrucksache.
        """
        super().__init__(model)

    def read_count_per_week(
        self,
        start_date: datetime.date,
        end_date: datetime.date,
        drucksachetyp_filter: list[str] | None = None,
        vorgangstyp_filter: list[str] | None = None,
    ) -> list[CountsPerWeek]:
        """Read the number of drucksachen per week. Used to check for complete data"""
        _logger.info("Read drucksachen-counts per week")
        data = CRUDBase.db.execute(
            sa.text(
                """
                    SELECT year, week, week_start_date, week_end_date, drucksache_count
                    FROM COUNT_WEEKLY_DRUCKSACHE(:start_date, :end_date, :drucksachetyp_filter, :vorgangstyp_filter);"""
            ),  # noqa: E501
            {
                "start_date": start_date,
                "end_date": end_date,
                "drucksachetyp_filter": drucksachetyp_filter,
                "vorgangstyp_filter": vorgangstyp_filter,
            },
        ).all()

        counts_per_week = []
        for row in data:
            counts_per_week.append(CountsPerWeek.model_validate(row._mapping))

        return counts_per_week


CRUD_DIP_DRUCKSACHE = CRUDDIPDrucksache(DIPDrucksache)
