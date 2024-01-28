import logging
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query

from backend.app.api.v1.models.messages import BundestagAbstimmungRedner
from backend.app.api.v1.models.queries import DateRange
from backend.app.services.abstimmung_redner.service import AbstimmungRednerService
from backend.app.services.common import ObjectNotFound
from typing import Annotated

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/abstimmung_redner", tags=["abstimmung_redner"])


@router.get(
    "/",
    response_model=list[BundestagAbstimmungRedner],
)
async def read_abstimmung_redner_multi(
    limit: int = 100,
    skip: int = 0,
    name: str | None = None,
    surname: str | None = None,
    abstimmung_id: Annotated[list[int], Query(..., alias="abstimmung_id")] = [],
    service: AbstimmungRednerService = Depends(AbstimmungRednerService),
):
    abstimmungen = (
        service.query(
            limit=limit,
            skip=skip,
            name=name,
            surname=surname,
            abstimmung_id=abstimmung_id,
        )
        or []
    )

    return abstimmungen


@router.get(
    "/count",
    response_model=int,
)
async def count_abstimmungen(
    name: str | None = None,
    surname: str | None = None,
    abstimmung_id: Annotated[list[int], Query(..., alias="abstimmung-id")] = [],
    service: AbstimmungRednerService = Depends(AbstimmungRednerService),
):
    return service.query_count(
        name=name,
        surname=surname,
        abstimmung_id=abstimmung_id,
    )


@router.get(
    "/{id}",
    response_model=BundestagAbstimmungRedner,
)
async def read_abstimmung_redner(
    id: int,
    service: AbstimmungRednerService = Depends(AbstimmungRednerService),
):
    msg = service.get(id=id)
    _logger.info(msg)

    if msg:
        return msg
    raise ObjectNotFound
