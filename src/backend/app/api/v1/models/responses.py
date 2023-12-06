import pydantic as pyd


class BundestagTopTopicsApiResponse(pyd.BaseModel):
    """Pydantic model for output."""

    month: int | None = pyd.Field(default=None)
    year: int | None = pyd.Field(default=None)
    election_period: int | None = pyd.Field(default=None)
    top_topics: dict[str, list] | None = pyd.Field(default=None)
