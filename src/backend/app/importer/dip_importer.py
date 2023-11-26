"""Class for DIP Bundestag Plenarprotokoll Importer."""

import logging

from backend.app.core.config import Settings
from backend.app.crud.base import CRUDBase
from backend.app.facades.deutscher_bundestag.facade import DIPBundestagFacade
from backend.app.facades.util import ProxyList
from backend.app.facades.deutscher_bundestag.model import Plenarprotokoll
from backend.app.facades.deutscher_bundestag.model_plenarprotokoll_vorgangsbezug import (
    PlenarprotokollVorgangsbezug,
)
from pydantic import BaseModel

from backend.app.crud.base import Base
from typing import Generic, TypeVar, Iterator, Mapping

_logger = logging.getLogger(__name__)


PydanticModelType = TypeVar("PydanticModelType", bound=BaseModel)  # pylint: disable=invalid-name
SQLModelType = TypeVar("SQLModelType", bound=Base)  # pylint: disable=invalid-name


ParamMapping = Mapping[str, str]


class DIPImporter(Generic[PydanticModelType, SQLModelType]):
    """Class for DIP Bundestag Importer."""

    def __init__(
        self,
        crud: CRUDBase[SQLModelType],
    ):
        """
        Initialize DIPImporter.
        """
        self.crud = crud
        self.dip_bundestag_facade = DIPBundestagFacade.get_instance(Settings())

    def transform_model(self, data: PydanticModelType) -> SQLModelType:
        """Transform data."""
        raise NotImplementedError

    def fetch_data(
        self,
        params: ParamMapping | None = None,
        response_limit=1000,
        proxy_list: ProxyList | None = None,
        *args,
        **kwargs,
    ) -> Iterator[PydanticModelType]:
        """Fetch data."""
        raise NotImplementedError

    def batch_upsert(
        self,
        params: ParamMapping | None = None,
        response_limit: int = 1000,
        proxy_list: ProxyList | None = None,
        upsert_batch_size: int = 100,
        *args,
        **kwargs,
    ):
        batch: list[SQLModelType] = []
        batch_count = 1
        for pydantic_model in self.fetch_data(
            params=params,
            response_limit=response_limit,
            proxy_list=proxy_list,
            *args,
            **kwargs,
        ):
            _logger.info(f'Adding model {pydantic_model} to batch.')
            sql_model = self.transform_model(pydantic_model)
            batch.append(sql_model)

            if len(batch) >= upsert_batch_size:
                _logger.info(f'Upserting batch {batch_count} into {sql_model.__tablename__}-Table.')
                self.crud.create_or_update_multi(batch)
                batch = []
                batch_count += 1

        if batch:
            _logger.info(
                f'Upserting final batch ({batch_count}) into {batch[0].__tablename__}-Table.'
            )
            self.crud.create_or_update_multi(batch)

    def import_data(
        self,
        params: ParamMapping | None = None,
        response_limit: int = 1000,
        proxy_list: ProxyList | None = None,
        upsert_batch_size: int = 100,
        *args,
        **kwargs,
    ):
        """Import data."""

        self.batch_upsert(
            params=params,
            response_limit=response_limit,
            proxy_list=proxy_list,
            upsert_batch_size=upsert_batch_size,
            *args,
            **kwargs,
        )
