"""top_topics relation for storing bundestag top topics of respective time frame."""
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.database import Base


class TopTopics(Base):
    """Table attributes for Model/Relation/Table top topics."""

    __tablename__ = "top_topics"
    id: Mapped[int] = mapped_column(primary_key=True)  # database id
    ressort: Mapped[str] = mapped_column(nullable=False)
    word: Mapped[str] = mapped_column(nullable=False)
    value: Mapped[str] = mapped_column(nullable=False)
    month: Mapped[int] = mapped_column(nullable=True)
    year: Mapped[int] = mapped_column(nullable=True)
    election_period: Mapped[int] = mapped_column(nullable=True)
