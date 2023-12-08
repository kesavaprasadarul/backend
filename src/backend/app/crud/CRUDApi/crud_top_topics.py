"""CRUD Operations TopTopics table."""
import logging

from backend.app.crud.base import CRUDBase
from backend.app.models.api.top_topics_model import TopTopics

_logger = logging.getLogger(__name__)


class CRUDTopTopics(CRUDBase[TopTopics]):
    """Provides CRUD operations for top_topics table."""

    def __init__(self, model: type):
        """
        Initialize CRUDExample.
        """
        test: str = "CrudTopTopics"  # dummy statement
        _logger.info("test: %s", test)  # dummy statement
        super().__init__(model)


CRUD_TOP_TOPICS = CRUDTopTopics(TopTopics)
