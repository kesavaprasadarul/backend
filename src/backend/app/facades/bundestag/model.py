from datetime import date
from enum import StrEnum
from typing import Optional

from pydantic import AnyUrl, BaseModel, Field

from backend.app.facades.facade import MediaType


class Vote(StrEnum):
    JA = "ja"
    NEIN = "nein"
    ENTHALTEN = "enthalten"
    NICHTABGEGEBEN = "nichtabgegeben"


class BundestagAbstimmungUrl(BaseModel):
    url: str = Field(
        description="Link to the vote.",
    )

    abstimmung_id: int = Field(
        description="ID of the vote.",
    )


class BundestagEinzelpersonAbstimmung(BaseModel):
    name: str = Field(
        description="Name of the person.",
    )

    surname: str = Field(
        description="Surname of the person.",
    )

    title: Optional[str] = Field(
        description="Title of the person.",
        default=None,
    )

    fraktion: str = Field(
        description="Party of the person.",
    )

    vote: Vote = Field(
        description="Vote of the person.",
    )

    bundesland: Optional[str] = Field(description="Bundesland of the person.", default=None)

    biography_url: AnyUrl = Field(
        description="Url to the biography of the person.",
    )

    image_url: Optional[AnyUrl] = Field(description="Url to the image of the person.", default=None)


class DIPRelatedDrucksache(BaseModel):
    url: AnyUrl = Field(
        description="Url to the Drucksache.",
    )

    drucksache_name: str = Field(
        description="Name of the Drucksache.",
    )


class BundestagAbstimmungRedner(BaseModel):
    name: str = Field(
        description="Name of the person.",
    )

    surname: str = Field(
        description="Surname of the person.",
    )

    title: Optional[str] = Field(
        description="Title of the person.",
        default=None,
    )

    function: str = Field(
        description="Function of the person.",
    )

    video_id: str = Field(
        description="ID of the video.",
    )

    video_url: AnyUrl = Field(
        description="Url to the video.",
    )

    image_url: AnyUrl = Field(
        description="Url to the image of the person.",
    )

    text: Optional[str] = Field(
        description="Text of the speech.",
        default=None,
    )


class BundestagAbstimmung(BaseModel):
    """Bundestag Abstimmung."""

    id: int = Field(
        description="ID of the vote.",
    )

    title: str = Field(
        description="Title of the vote.",
    )

    abstimmung_date: date = Field(
        description="Date of the vote.",
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

    nicht_abgegeben: int = Field(
        description="Number of votes not cast.",
    )

    individual_votes: list[BundestagEinzelpersonAbstimmung] = Field(
        description="List of individual votes.",
    )

    drucksachen: list[DIPRelatedDrucksache] = Field(
        description="List of related Drucksachen.",
    )

    dachzeile: Optional[str] = Field(
        description="Headline of the vote.",
    )

    redner: list[BundestagAbstimmungRedner] = Field(
        description="List of speakers.",
    )
