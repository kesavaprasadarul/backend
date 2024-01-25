"""top_topics relation for storing bundestag top topics of respective time frame."""
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.database import Base


class TopTopics(Base):
    """Table attributes for Model/Relation/Table top topics."""

    __tablename__ = "top_topics"

    month: Mapped[int] = mapped_column(primary_key=True)
    year: Mapped[int] = mapped_column(primary_key=True)
    election_period: Mapped[int] = mapped_column(primary_key=True)
    ressort: Mapped[str] = mapped_column(nullable=False)
    index: Mapped[int] = mapped_column(primary_key=True)
    word: Mapped[str] = mapped_column(nullable=False)
    value: Mapped[str] = mapped_column(nullable=False)
