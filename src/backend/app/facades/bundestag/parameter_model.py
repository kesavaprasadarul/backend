from pydantic import BaseModel, Field, field_serializer
from typing import Optional
from datetime import date, datetime


class BundestagAbstimmungenPointerParameter(BaseModel):
    """Bundestag Abstimmungen Pointer."""

    date_start: Optional[date] = Field(
        default=None,
        description="Frühestes Datum der Entität",
        serialization_alias="startdate",
    )

    date_end: Optional[date] = Field(
        default=None,
        description="Spätestes Datum der Entität",
        serialization_alias="enddate",
    )

    @field_serializer('date_start', 'date_end')
    def serialize_aktualisiert(self, value: date) -> str:
        """Serialize aktualisiert_start and aktualisiert_end in a format that is accepted by the API."""
        return str(int(datetime(value.year, value.month, value.day).timestamp())).ljust(13, '0')


class BundestagAbstimmungParameter(BaseModel):
    abstimmung_id: int = Field(description="ID of the vote.", serialization_alias="id")


class BundestagRedeParameter(BaseModel):
    video_id: str = Field(
        description="ID of the video with which to fetch the subtitles.",
        serialization_alias="content",
    )
