"""Class for DIP Bundestag Plenarprotokoll Importer."""

import logging
from typing import Any, Generic, Iterator, MutableMapping, Optional, TypeVar

from pydantic import BaseModel

from backend.app.core.config import Settings
from backend.app.crud.base import Base, CRUDBase
from backend.app.facades.deutscher_bundestag.facade import DIPBundestagFacade
from backend.app.facades.util import ProxyList

_logger = logging.getLogger(__name__)


PydanticDataModelType = TypeVar(
    "PydanticDataModelType", bound=BaseModel
)  # pylint: disable=invalid-name
PydanticParameterModelType = TypeVar(
    "PydanticParameterModelType", bound=BaseModel
)  # pylint: disable=invalid-name

SQLModelType = TypeVar("SQLModelType", bound=Base)  # pylint: disable=invalid-name


ParamMapping = MutableMapping


class DIPImporter(Generic[PydanticDataModelType, PydanticParameterModelType, SQLModelType]):
    """Class for DIP Bundestag Importer."""

    def __init__(
        self,
        crud: CRUDBase[SQLModelType],
    ):
        """
        Initialize DIPImporter.
        """
        self.crud = crud
        self.imported_count = 0
        self.dip_bundestag_facade = DIPBundestagFacade.get_instance(Settings())

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
    ) -> Iterator[SQLModelType]:
        """Fetch data."""
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
        ):
            batch.append(db_model)

            if len(batch) >= upsert_batch_size:
                _logger.info(f'Upserting batch {batch_number} into {db_model.__tablename__}-Table.')
                self.crud.create_or_update_multi(batch)
                batch = []
                batch_number += 1
                self.imported_count += upsert_batch_size

        if batch:
            _logger.info(
                f'Upserting final batch ({batch_number}) into {batch[0].__tablename__}-Table.'
            )
            self.crud.create_or_update_multi(batch)
            self.imported_count += len(batch)

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
