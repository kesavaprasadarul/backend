"""CRUD Operations GitHubOrganization"""
import logging

from backend.app.crud.base import CRUDBase
from backend.app.models.vorgang_model import VorgangModel

_logger = logging.getLogger(__name__)


class CRUDVorgang(CRUDBase[VorgangModel]):
    """Provides CRUD operations for vorgang table."""

    def __init__(self, model: type):
        """
        Initialize CRUDExample.
        """
        test: str = "vorgangExample"  # dummy statement
        _logger.info("test: %s", test)  # dummy statement
        super().__init__(model)


CRUD_VORGANG = CRUDVorgang(VorgangModel)
