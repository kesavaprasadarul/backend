from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from backend.app.facades.facade import MediaType
from enum import StrEnum


class Vote(StrEnum):
    JA = "ja"
    NEIN = "nein"
    ENTHALTEN = "enthalten"
    UNGUELTIG = "ungueltig"
    NICHTABGEGEBEN = "nichtabgegeben"


class BundestagAbstimmungLink(BaseModel):
    type: MediaType = Field(
        description="Type of the link.",
    )
    url: str = Field(
        description="URL of the link.",
    )


class BundestagAbstimmungLinks(BaseModel):
    """Bundestag Abstimmungen Links."""

    publication_date: Optional[datetime] = Field(
        None,
        description="Publication date of the document.",
    )

    title: str = Field(
        description="Title of the document.",
    )

    abstimmung_date: datetime = Field(
        description="Date of the vote.",
    )

    links: list[BundestagAbstimmungLink] = Field(
        description="List of links.",
    )


class BundestagEinzelpersonAbstimmung(BaseModel):
    name: str = Field(
        description="Name of the person.",
    )

    surname: str = Field(
        description="Surname of the person.",
    )

    fraktion: str = Field(
        description="Party of the person.",
    )

    vote: Vote = Field(
        description="Vote of the person.",
    )


class BundestagAbstimmung(BaseModel):
    """Bundestag Abstimmung."""

    title: str = Field(
        description="Title of the vote.",
    )

    abstimmung_date: datetime = Field(
        description="Date of the vote.",
    )

    wahlperiode: int = Field(
        description="Legislative period.",
    )

    sitzung: int = Field(
        description="Session.",
    )

    abstimmung_number: int = Field(
        description="Number of the vote.",
    )

    ja: int = Field(
        description="Number of yes votes.",
    )

    nein: int = Field(
        description="Number of no votes.",
    )

    enthalten: int = Field(
        description="Number of abstentions.",
    )

    ungueltig: int = Field(
        description="Number of invalid votes.",
    )

    nicht_abgegeben: int = Field(
        description="Number of votes not cast.",
    )

    links: list[BundestagAbstimmungLink] = Field(
        description="List of links.",
    )

    votes: list[BundestagEinzelpersonAbstimmung] = Field(
        description="List of votes.",
    )

    link_used: BundestagAbstimmungLink = Field(
        description="Link used to retrieve the data.",
    )
