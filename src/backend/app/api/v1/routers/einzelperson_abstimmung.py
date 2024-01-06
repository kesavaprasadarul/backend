"""Contains endpoints for importing PLENARPROTOKOLLE from DIP Bundestag API with DIP Bundestag facade."""
import logging
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends

from backend.app.api.v1.models.messages import BundestagEinzelpersonAbstimmung
from backend.app.api.v1.models.queries import DateRange
from backend.app.services.einzelperson_abstimmung.service import EinzelpersonAbstimmungService
from backend.app.services.common import ObjectNotFound

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/einzelperson-abstimmung", tags=["einzelperson-abstimmung"])


@router.get(
    "/",
    response_model=list[BundestagEinzelpersonAbstimmung],
)
async def read_einzelperson_abstimmungen(
    limit: int = 100,
    abstimmung_id: int | None = None,
    person_id: int | None = None,
    name: str | None = None,
    surname: str | None = None,
    fraction: str | None = None,
    service: EinzelpersonAbstimmungService = Depends(EinzelpersonAbstimmungService),
):
    abstimmungen = (
        service.query(
            limit=limit,
            skip=0,
            abstimmung_id=abstimmung_id,
            person_id=person_id,
            name=name,
            surname=surname,
            fraktion=fraction,
        )
        or []
    )

    return abstimmungen


@router.get(
    "/count",
    response_model=int,
)
async def count_einzelperson_abstimmungen(
    abstimmung_id: int | None = None,
    person_id: int | None = None,
    name: str | None = None,
    surname: str | None = None,
    fraction: str | None = None,
    service: EinzelpersonAbstimmungService = Depends(EinzelpersonAbstimmungService),
):
    return service.query_count(
        abstimmung_id=abstimmung_id,
        person_id=person_id,
        name=name,
        surname=surname,
        fraktion=fraction,
    )


@router.get(
    "/{id}",
    response_model=BundestagEinzelpersonAbstimmung,
)
async def read_einzelperson_abstimmung(
    id: int,
    service: EinzelpersonAbstimmungService = Depends(EinzelpersonAbstimmungService),
):
    msg = service.get(id=id)
    _logger.info(msg)

    if msg:
        return msg
    raise ObjectNotFound
