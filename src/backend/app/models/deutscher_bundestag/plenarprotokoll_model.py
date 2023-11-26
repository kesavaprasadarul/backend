"""Deutscher Bundestag Drucksache SQLAlchemy Models for creating associated tables in database."""
import datetime

from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.database import Base


class DIPPlenarprotokoll(Base):
    """Table attributes for Model/Relation/Table plenarprotokoll."""

    __tablename__ = "plenarprotokoll"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id
    dokumentart: Mapped[str] = mapped_column(nullable=False)
    typ: Mapped[str] = mapped_column(nullable=False)
    dokumentnummer: Mapped[str] = mapped_column(nullable=False)
    wahlperiode: Mapped[int] = mapped_column(nullable=True)
    herausgeber: Mapped[str] = mapped_column(nullable=False)
    date: Mapped[str] = mapped_column(nullable=True)
    datum: Mapped[datetime.date] = mapped_column(nullable=False)
    aktualisiert: Mapped[str] = mapped_column(nullable=False)
    titel: Mapped[str] = mapped_column(nullable=False)
    pdf_hash: Mapped[str] = mapped_column(nullable=True)
    vorgangsbezug_anzahl: Mapped[int] = mapped_column(nullable=False)


class DIPPlenarprotokollVorgangsbezug(Base):
    """Table attributes for Model/Relation/Table plenarprotokoll vorgangsbezug."""

    __tablename__ = "plenarprotokoll_vorgangsbezug"

    id: Mapped[int] = mapped_column(primary_key=True)
    plenarprotokoll_id: Mapped[int] = mapped_column(nullable=True)
    titel: Mapped[str] = mapped_column(nullable=False)
    abstract: Mapped[str] = mapped_column(nullable=False)
    datum: Mapped[datetime.date] = mapped_column(nullable=False)
