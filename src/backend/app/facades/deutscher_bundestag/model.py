"""Data model used by DIP Bundestag facade."""
import pydantic as pyd


class DIPBundestagApiDrucksache(pyd.BaseModel):
    """Servicedesk internal representation of a Servicedesk Issue."""

    drucksache_id: int = pyd.Field(alias='id')
    drucksache_type: str = pyd.Field(alias='drucksachetyp')
    document_type: str = pyd.Field(alias='dokumentart')
    document_number: str = pyd.Field(alias='dokumentnummer')
    voting_period: int = pyd.Field(alias='wahlperiode')
    author: str = pyd.Field(alias='herausgeber')
    last_updated: str = pyd.Field(alias='aktualisiert')
    title: str = pyd.Field(alias='titel')
    date: str = pyd.Field(alias='datum')
    text: str | None = pyd.Field(default=None)
