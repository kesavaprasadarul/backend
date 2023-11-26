"""Extra pydantic model for Vorgangsbezuege of Plenarprotokoll."""

import datetime

import pydantic as pyd


class PlenarprotokollVorgangsbezug(pyd.BaseModel):
    """Model for plenarprotkoll vorgangsbezug."""

    id: int = pyd.Field()
    titel: str
    abstract: str
    datum: datetime.date
