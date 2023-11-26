"""Deutscher Bundestag Drucksache SQLAlchemy Models for creating associated tables in database."""
import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from backend.app.db.database import Base

from backend.app.models.deutscher_bundestag.common import DIPSchema, TimestampMixin
from backend.app.models.deutscher_bundestag.fundstelle_model import DIPFundstelle
from backend.app.models.deutscher_bundestag.vorgangsbezug_model import DIPVorgangsbezug


class DIPPlenarprotokoll(Base, DIPSchema, TimestampMixin):
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

    fundstelle: Mapped["DIPFundstelle"] = relationship(
        cascade='merge, save-update, delete, delete-orphan',
        back_populates="plenarprotokoll",
        foreign_keys="DIPFundstelle.plenarprotokoll_id",
    )

    vorgangsbezug: Mapped[list["DIPVorgangsbezug"]] = relationship(
        cascade='merge, save-update, delete, delete-orphan',
        foreign_keys="DIPVorgangsbezug.plenarprotokoll_id",
    )

    plenarprotokoll_text: Mapped["DIPPlenarprotokollText"] = relationship(
        cascade='merge, save-update, delete, delete-orphan',
        back_populates="plenarprotokoll",
    )


class DIPPlenarprotokollText(Base, TimestampMixin, DIPSchema):
    __tablename__ = "plenarprotokoll_text"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id
    plenarprotokoll_id: Mapped[int] = mapped_column(
        ForeignKey("dip.plenarprotokoll.id"), nullable=False
    )
    text: Mapped[str] = mapped_column(nullable=False)

    plenarprotokoll: Mapped["DIPPlenarprotokoll"] = relationship(
        "DIPPlenarprotokoll", back_populates="plenarprotokoll_text"
    )
