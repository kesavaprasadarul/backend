"""CRUD Operations DIP Bundestag for Drucksache."""
import logging

from backend.app.crud.base import CRUDBase
from backend.app.models.example_model import ExampleModel

_logger = logging.getLogger(__name__)


class CRUDDIPDrucksache(CRUDBase[ExampleModel]):
    """Provides CRUD operations for example_model table."""

    def __init__(self, model: type):
        """
        Initialize CRUDExample.
        """
        test: str = "CrudExample"  # dummy statement
        _logger.info("test: %s", test)  # dummy statement
        super().__init__(model)


CRUD_EXAMPLE = CRUDDIPDrucksache(ExampleModel)
