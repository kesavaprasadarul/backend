"""Contains endpoints for importing PLENARPROTOKOLLE from DIP Bundestag API with DIP Bundestag facade."""
import logging
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends

from backend.app.api.v1.models.messages import Beschlussfassung
from backend.app.api.v1.models.queries import DateRange, DatetimeRange
from backend.app.services.beschlussfassung.service import BeschlussfassungService
from backend.app.services.common import ObjectNotFound

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/beschlussfassung", tags=["beschlussfassung"])


@router.get(
    "/",
    response_model=list[Beschlussfassung],
)
async def read_beschlussfassungen(
    limit: int = 100,
    date_min: date | None = None,
    date_max: date | None = None,
    aktualisiert_min: datetime | None = None,
    aktualisiert_max: datetime | None = None,
    service: BeschlussfassungService = Depends(BeschlussfassungService),
):
    abstimmungen = (
        service.query(
            limit=limit,
            skip=0,
            datum=DateRange(min=date_min, max=date_max),
            aktualisiert=DatetimeRange(min=aktualisiert_min, max=aktualisiert_max),
        )
        or []
    )

    return abstimmungen


@router.get(
    "/count",
    response_model=int,
)
async def count_abstimmungen(
    date_min: date | None = None,
    date_max: date | None = None,
    aktualisiert_min: datetime | None = None,
    aktualisiert_max: datetime | None = None,
    service: BeschlussfassungService = Depends(BeschlussfassungService),
):
    return service.query_count(
        datum=DateRange(min=date_min, max=date_max),
        aktualisiert=DatetimeRange(min=aktualisiert_min, max=aktualisiert_max),
    )


@router.get(
    "/{id}",
    response_model=Beschlussfassung,
)
async def read_abstimmung(
    id: int,
    service: BeschlussfassungService = Depends(BeschlussfassungService),
):
    msg = service.get(id=id)
    _logger.info(msg)

    if msg:
        return msg
    raise ObjectNotFound
