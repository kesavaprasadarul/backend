import datetime as dt

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.database import Base
from backend.app.facades.deutscher_bundestag.model import Dokumentart, Quadrant, Zuordnung
from backend.app.models.common import DIPSchema, TimestampMixin

# from backend.app.models.deutscher_bundestag.drucksache_model import DIPDrucksache
# from backend.app.models.deutscher_bundestag.vorgangsposition_model import DIPVorgangsposition


class DIPFundstelle(Base, TimestampMixin, DIPSchema):
    __tablename__ = "fundstelle"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id

    drucksache_id: Mapped[int] = mapped_column(ForeignKey(f"dip.drucksache.id"), nullable=True)

    vorgangsposition_id: Mapped[int] = mapped_column(
        ForeignKey(f"dip.vorgangsposition.id"),
        nullable=True,
    )

    plenarprotokoll_id: Mapped[int] = mapped_column(
        ForeignKey(f"dip.plenarprotokoll.id"),
        nullable=True,
    )

    dokumentart: Mapped[Dokumentart] = mapped_column(nullable=False)
    pdf_url: Mapped[str] = mapped_column(nullable=True)
    dokumentnummer: Mapped[str] = mapped_column(nullable=False)
    datum: Mapped[dt.date] = mapped_column(nullable=False)
    drucksachetyp: Mapped[str] = mapped_column(nullable=True)
    herausgeber: Mapped[Zuordnung] = mapped_column(nullable=False)
    urheber: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)
    verteildatum: Mapped[dt.datetime] = mapped_column(nullable=True)
    seite: Mapped[str] = mapped_column(nullable=True)
    anfangsseite: Mapped[int] = mapped_column(nullable=True)
    endseite: Mapped[int] = mapped_column(nullable=True)
    anfangsquadrant: Mapped[Quadrant] = mapped_column(nullable=True)
    endquadrant: Mapped[Quadrant] = mapped_column(nullable=True)
    frage_nummer: Mapped[str] = mapped_column(nullable=True)
    anlagen: Mapped[str] = mapped_column(nullable=True)
    top: Mapped[int] = mapped_column(nullable=True)
    top_zusatz: Mapped[str] = mapped_column(nullable=True)

    drucksache = relationship("DIPDrucksache", back_populates="fundstelle")

    vorgangsposition = relationship("DIPVorgangsposition", back_populates="fundstelle")

    plenarprotokoll = relationship("DIPPlenarprotokoll", back_populates="fundstelle")
