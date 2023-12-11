from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class Abstimmung(BaseModel):
    """Eine Abstimmung."""

    id: int

    titel: str
    abstimmung_datum: date
    akzeptiert: bool
    ja: int
    nein: int
    enthalten: int
    nicht_abgegeben: int

    aktualisiert: datetime

    class Config:
        from_attributes = True


class BundestagTopTopic(BaseModel):
    """Eine Top Topoic."""

    id: int

    ressort: str
    word: str
    value: int
    month: Optional[int]
    year: Optional[int]
    election_period: Optional[int]

    class Config:
        from_attributes = True
