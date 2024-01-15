"""Contains endpoints for importing PLENARPROTOKOLLE from DIP Bundestag API with DIP Bundestag facade."""
import logging
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query

from backend.app.api.v1.models.messages import BundestagAbstimmung
from backend.app.api.v1.models.queries import DateRange
from backend.app.services.abstimmung.service import AbstimmungService
from backend.app.services.common import ObjectNotFound
from typing import Annotated

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/abstimmung", tags=["abstimmung"])


@router.get(
    "/",
    response_model=list[BundestagAbstimmung],
)
async def read_abstimmungen(
    limit: int = 100,
    skip: int = 0,
    date_min: date | None = None,
    date_max: date | None = None,
    dachzeile: Annotated[list[str], Query(..., alias="dachzeile")] = [],
    service: AbstimmungService = Depends(AbstimmungService),
):
    abstimmungen = (
        service.query(
            limit=limit,
            skip=skip,
            datum=DateRange(min=date_min, max=date_max),
            dachzeile=dachzeile,
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
    dachzeile: Annotated[list[str], Query(..., alias="dachzeile")] = [],
    service: AbstimmungService = Depends(AbstimmungService),
):
    return service.query_count(datum=DateRange(min=date_min, max=date_max), dachzeile=dachzeile)


@router.get(
    "/{id}",
    response_model=BundestagAbstimmung,
)
async def read_abstimmung(
    id: int,
    service: AbstimmungService = Depends(AbstimmungService),
):
    msg = service.get(id=id)
    _logger.info(msg)

    if msg:
        return msg
    raise ObjectNotFound
