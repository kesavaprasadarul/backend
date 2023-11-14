"""Deutscher Bundestag Drucksache SQLAlchemy Models for creating associated tables in database."""
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.database import Base


class DIPDrucksache(Base):
    """Table attributes for Model/Relation/Table example_model."""

    __tablename__ = "dip_drucksache"
    drucksache_id: Mapped[int] = mapped_column(primary_key=True)  # database id
    drucksache_type: Mapped[str] = mapped_column(nullable=True)
    document_type: Mapped[str] = mapped_column(nullable=True)
    document_number: Mapped[str] = mapped_column(nullable=True)
    voting_period: Mapped[int] = mapped_column(nullable=True)
    author: Mapped[str] = mapped_column(nullable=True)
    last_updated: Mapped[str] = mapped_column(nullable=True)
    title: Mapped[str] = mapped_column(nullable=True)
    date: Mapped[str] = mapped_column(nullable=True)
    text: Mapped[str] = mapped_column(nullable=True)
