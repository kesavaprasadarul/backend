"""Base class for HTTP-Imports."""

import logging
from typing import Any, Generic, Iterator, MutableMapping, Optional, TypeVar

from pydantic import BaseModel

from backend.app.core.config import Settings
from backend.app.crud.base import Base, CRUDBase
from backend.app.facades.deutscher_bundestag.facade import HttpFacade
from backend.app.facades.util import ProxyList

_logger = logging.getLogger(__name__)


PydanticDataModelType = TypeVar(
    "PydanticDataModelType", bound=BaseModel
)  # pylint: disable=invalid-name
PydanticParameterModelType = TypeVar(
    "PydanticParameterModelType", bound=BaseModel
)  # pylint: disable=invalid-name

FacadeType = TypeVar("FacadeType", bound=HttpFacade)  # pylint: disable=invalid-name

SQLModelType = TypeVar("SQLModelType", bound=Base)  # pylint: disable=invalid-name


ParamMapping = MutableMapping

DELAY_BETWEEN_REQUESTS = 0.5


class HttpImporter(
    Generic[FacadeType, PydanticDataModelType, PydanticParameterModelType, SQLModelType]
):
    """Class for HTTP Imports."""

    def __init__(
        self,
        crud: CRUDBase[SQLModelType],
        facade: FacadeType,
        delay_between_requests: float = DELAY_BETWEEN_REQUESTS,
    ):
        """
        Initialize DIPImporter.
        """
        self.crud = crud
        self.imported_count = 0
        self.facade = facade
        self.delay_between_requests = delay_between_requests

    def get_imported_count(self) -> int:
        """Get count of imported data."""
        return self.imported_count

    def transform_model(self, data: PydanticDataModelType) -> SQLModelType:
        """Transform data."""
        raise NotImplementedError

    def fetch_data(
        self,
        params: Optional[PydanticParameterModelType] = None,
        response_limit=1000,
        proxy_list: ProxyList | None = None,
        **kwargs: Any,
    ) -> Iterator[SQLModelType]:
        """Fetch data."""
        raise NotImplementedError

    def fetch_count(
        self,
        params: Optional[PydanticParameterModelType] = None,
        proxy_list: ProxyList | None = None,
    ) -> int:
        """Fetch count."""
        raise NotImplementedError

    def batch_upsert(
        self,
        params: Optional[PydanticParameterModelType] = None,
        response_limit: int = 1000,
        proxy_list: ProxyList | None = None,
        upsert_batch_size: int = 100,
        **kwargs: Any,
    ):
        batch: list[SQLModelType] = []
        batch_number = 0
        for db_model in self.fetch_data(
            params=params,
            response_limit=response_limit,
            proxy_list=proxy_list,
            **kwargs,
        ):
            batch.append(db_model)

            if len(batch) >= upsert_batch_size:
                _logger.debug(
                    f'Upserting batch {batch_number} into {db_model.__tablename__}-Table.'
                )
                self.crud.create_or_update_multi(batch)
                batch = []
                batch_number += 1
                self.imported_count += upsert_batch_size

        if batch:
            _logger.debug(
                f'Upserting final batch ({batch_number}) into {batch[0].__tablename__}-Table.'
            )
            self.crud.create_or_update_multi(batch)
            self.imported_count += len(batch)

        _logger.debug(f'Imported {self.imported_count} {self.crud.model.__tablename__}.')

    def import_data(
        self,
        params: Optional[PydanticParameterModelType] = None,
        response_limit: int = 1000,
        proxy_list: ProxyList | None = None,
        upsert_batch_size: int = 100,
        **kwargs,
    ):
        """Import data."""

        self.batch_upsert(
            params=params,
            response_limit=response_limit,
            proxy_list=proxy_list,
            upsert_batch_size=upsert_batch_size,
            **kwargs,
        )
