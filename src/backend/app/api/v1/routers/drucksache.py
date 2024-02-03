"""Contains endpoints for importing PLENARPROTOKOLLE from DIP Bundestag API with DIP Bundestag facade."""
import logging
from datetime import date, datetime

from fastapi import APIRouter, Depends, Query, HTTPException
from backend.app.api.v1.models.messages import Drucksache
from backend.app.api.v1.models.queries import DateRange, DatetimeRange
from backend.app.services.drucksache.service import DrucksacheService
from backend.app.services.common import ObjectNotFound
from typing import Annotated

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/drucksache", tags=["drucksache"])


@router.get(
    "/",
    response_model=list[Drucksache],
)
async def read_drucksachen(
    limit: int = 100,
    skip: int = 0,
    date_min: date | None = None,
    date_max: date | None = None,
    aktualisiert_min: datetime | None = None,
    aktualisiert_max: datetime | None = None,
    drucksache_ids: Annotated[list[int], Query(..., alias="drucksache_ids")] = [],
    service: DrucksacheService = Depends(DrucksacheService),
):
    if limit > 200:
        raise HTTPException(status_code=400, detail="Limit cannot exceed 200")

    drucksachen = (
        service.query(
            limit=limit,
            skip=skip,
            datum=DateRange(min=date_min, max=date_max),
            aktualisiert=DatetimeRange(min=aktualisiert_min, max=aktualisiert_max),
            drucksache_ids=drucksache_ids,
        )
        or []
    )

    return drucksachen


@router.get(
    "/count",
    response_model=int,
)
async def count_abstimmungen(
    date_min: date | None = None,
    date_max: date | None = None,
    aktualisiert_min: datetime | None = None,
    aktualisiert_max: datetime | None = None,
    service: DrucksacheService = Depends(DrucksacheService),
):
    return service.query_count(
        datum=DateRange(min=date_min, max=date_max),
        aktualisiert=DatetimeRange(min=aktualisiert_min, max=aktualisiert_max),
    )


@router.get(
    "/{id}",
    response_model=Drucksache,
)
async def read_abstimmung(
    id: int,
    service: DrucksacheService = Depends(DrucksacheService),
):
    msg = service.get(id=id)
    _logger.info(msg)

    if msg:
        return msg
    raise ObjectNotFound
