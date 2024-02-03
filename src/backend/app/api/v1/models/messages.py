from datetime import date, datetime
from enum import Enum
from typing import Optional

from backend.app.facades.bundestag.model import Vote

from pydantic import BaseModel


class Verkuendung(BaseModel):
    """Eine Verkündung."""

    id: int
    fundstelle: str
    pdf_url: Optional[str]
    typ: Optional[str]

    class Config:
        from_attributes = True


class Vorgang(BaseModel):
    """Ein Vorgang."""

    vorgang_id: int
    vorgangstyp: str
    titel: str
    abstract: Optional[str]
    sachgebiet: list[str]
    verkuendungen: list[Verkuendung]
    deskriptoren: list[str]

    class Config:
        from_attributes = True


class Drucksache(BaseModel):
    """Eine Drucksache."""

    id: int
    drucksachetyp: str
    drucksache_name: str
    pdf_url: str
    titel: str
    datum: date
    ressorts: list[str]

    vorgaenge: list[Vorgang]

    class Config:
        from_attributes = True


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

    ressort: str
    word: str
    value: int
    index: int
    month: Optional[int]
    year: Optional[int]
    election_period: Optional[int]

    class Config:
        from_attributes = True


class BundestagAbstimmungDrucksache(BaseModel):
    """Eine Drucksache zu einer Abstimmung."""

    drucksache_name: str
    drucksache_url: str
    drucksache_id: int

    class Config:
        from_attributes = True


class BundestagFraktionAbstimmung(BaseModel):
    """Eine Abstimmung einer Fraktion."""

    fraktion: str

    ja: int
    nein: int
    enthalten: int
    nicht_abgegeben: int

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

    fraktionen: list[BundestagFraktionAbstimmung]

    class Config:
        from_attributes = True


class BundestagRede(BaseModel):
    bt_video_id: str
    video_url: str
    text: str


class BundestagAbstimmungRedner(BaseModel):
    id: int
    abstimmung_id: int
    full_name: str
    function: str
    image_url: Optional[str]
    reden: list[BundestagRede]


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
