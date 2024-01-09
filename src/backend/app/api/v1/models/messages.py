from datetime import date, datetime
from enum import Enum
from typing import Optional

from backend.app.facades.bundestag.model import Vote

from pydantic import BaseModel


class Beschlussfassung(BaseModel):
    """Eine Beschlussfassung."""

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


class BundestagAbstimmungDrucksache(BaseModel):
    """Eine Drucksache zu einer Abstimmung."""

    drucksache_name: str
    drucksache_url: str

    class Config:
        from_attributes = True


class BundestagAbstimmung(BaseModel):
    id: int

    titel: str
    abstimmung_date: date

    ja: int
    nein: int
    enthalten: int
    nicht_abgegeben: int

    dachzeile: Optional[str]

    drucksachen: list[BundestagAbstimmungDrucksache]

    class Config:
        from_attributes = True


class BundestagAbstimmungReden(BaseModel):
    bt_video_id: int
    video_url: str
    text: str


class BundestagEinzelpersonAbstimmung(BaseModel):
    id: int

    person_id: int
    abstimmung_id: int

    nachname: str
    vorname: str
    titel: Optional[str]

    fraktion: str

    vote: Vote

    image_url: Optional[str]
