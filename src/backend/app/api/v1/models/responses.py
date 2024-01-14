import pydantic as pyd
from backend.app.core.bundestag_ressorts import BUNDESTAG_RESSORT


class BundestagTopTopicsApiResponse(pyd.BaseModel):
    """Pydantic model for output."""

    month: int | None = pyd.Field(default=None)
    year: int | None = pyd.Field(default=None)
    election_period: int | None = pyd.Field(default=None)
    top_topics: dict[BUNDESTAG_RESSORT, list] | None = pyd.Field(default=None)
