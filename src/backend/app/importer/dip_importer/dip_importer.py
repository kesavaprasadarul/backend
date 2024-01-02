"""Class for DIP Bundestag Plenarprotokoll Importer."""

import logging
from typing import Any, Generic, Iterator, MutableMapping, Optional, TypeVar

from pydantic import BaseModel

from backend.app.core.config import Settings
from backend.app.crud.base import Base, CRUDBase
from backend.app.facades.deutscher_bundestag.facade import DIPBundestagFacade
from backend.app.facades.util import ProxyList
from backend.app.importer.base import HttpImporter


PydanticDataModelType = TypeVar(
    "PydanticDataModelType", bound=BaseModel
)  # pylint: disable=invalid-name
PydanticParameterModelType = TypeVar(
    "PydanticParameterModelType", bound=BaseModel
)  # pylint: disable=invalid-name

SQLModelType = TypeVar("SQLModelType", bound=Base)  # pylint: disable=invalid-name


ParamMapping = MutableMapping

DELAY_BETWEEN_REQUESTS = 0.5


class DIPImporter(
    HttpImporter[
        DIPBundestagFacade, PydanticDataModelType, PydanticParameterModelType, SQLModelType
    ]
):
    """Class for DIP Bundestag Importer."""

    def __init__(
        self,
        crud: CRUDBase[SQLModelType],
        delay_between_requests: float = DELAY_BETWEEN_REQUESTS,
    ):
        """
        Initialize DIPImporter.
        """
        super().__init__(
            crud=crud,
            facade=DIPBundestagFacade.get_instance(Settings()),
            delay_between_requests=delay_between_requests,
        )
