"""ROUTES for GitHub"""
import logging

import fastapi

import backend.app.schemas.schema_example as schema_example  # pylint: disable=consider-using-from-import
from backend.app.crud.crud_example import CRUD_EXAMPLE

_logger = logging.getLogger(__name__)

router = fastapi.APIRouter()


@router.get(
    "/example",
    response_model=list[schema_example.Example],
    tags=["example"],
)
def read_example():
    _logger.info('Read all from model_example.')
    return CRUD_EXAMPLE.read_all()
