"""CRUD Operations Bundestag Einzelperson Abstimmung."""
import datetime
import logging

from pydantic import BaseModel
from sqlalchemy.exc import OperationalError
from backend.app.crud.base import CRUDBase
from backend.app.models.bundestag.abstimmung_model import BTEinzelpersonAbstimmung

_logger = logging.getLogger(__name__)


class CRUDBundestagEinzelpersonAbstimmung(CRUDBase[BTEinzelpersonAbstimmung]):
    """Provides CRUD operations for bt.einzelperson_abstimmung table."""

    def __init__(self, model: type):
        """
        Initialize CRUDDIPDrucksache.
        """
        super().__init__(model)

    def read_person_filtered_count(self, base_filters: list = [], person_filters: list = []) -> int:
        """Count objects from database."""
        try:
            return (
                CRUDBase.db.query(self.model)
                .filter(*base_filters)
                .join(BTEinzelpersonAbstimmung.person)
                .filter(*person_filters)
                .count()
            )
        except OperationalError as error:
            # if database closed unexpectedly, OperationalError occurs
            _logger.error("%s occured. Session will be rolled back.", error)
            CRUDBase.db.rollback()
            return (
                CRUDBase.db.query(self.model)
                .filter(*base_filters)
                .join(BTEinzelpersonAbstimmung.person)
                .filter(*person_filters)
                .count()
            )

    def read_person_filtered_multi(
        self,
        limit: int,
        skip: int = 0,
        base_filters: list = [],
        person_filters: list = [],
    ) -> list[BTEinzelpersonAbstimmung]:
        """Query objects from database."""
        try:
            return (
                CRUDBase.db.query(self.model)
                .filter(*base_filters)
                .join(BTEinzelpersonAbstimmung.person)
                .filter(*person_filters)
                .order_by(BTEinzelpersonAbstimmung.abstimmung_id)
                .offset(skip)
                .limit(limit)
                .all()
            )
        except OperationalError as error:
            # if database closed unexpectedly, OperationalError occurs
            _logger.error("%s occured. Session will be rolled back.", error)
            CRUDBase.db.rollback()
            return (
                CRUDBase.db.query(self.model)
                .filter(*base_filters)
                .join(BTEinzelpersonAbstimmung.person)
                .filter(*person_filters)
                .order_by(BTEinzelpersonAbstimmung.abstimmung_id)
                .offset(skip)
                .limit(limit)
                .all()
            )


CRUD_BUNDESTAG_EINZELPERSON_ABSTIMMUNG = CRUDBundestagEinzelpersonAbstimmung(
    BTEinzelpersonAbstimmung
)
