"""Deutscher Bundestag Drucksache SQLAlchemy Models for creating associated tables in database."""
import datetime as dt

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.database import Base
from backend.app.facades.deutscher_bundestag.model import (
    DokumentartDrucksache,
    DokumentTyp,
    Herausgeber,
)
from backend.app.models.config import SchemaNames
from backend.app.models.deutscher_bundestag.common import DIPSchema, TimestampMixin
from backend.app.models.deutscher_bundestag.fundstelle_model import DIPFundstelle
from backend.app.models.deutscher_bundestag.ressort_model import DIPRessort
from backend.app.models.deutscher_bundestag.urheber_model import DIPUrheber
from backend.app.models.deutscher_bundestag.vorgangsbezug_model import DIPVorgangsbezug


class DIPDrucksache(Base, TimestampMixin, DIPSchema):
    """Table attributes for Model/Relation/Table drucksache."""

    __tablename__ = "drucksache"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id
    typ: Mapped[DokumentTyp] = mapped_column(nullable=False)
    dokumentart: Mapped[DokumentartDrucksache] = mapped_column(nullable=False)
    drucksachetyp: Mapped[str] = mapped_column(nullable=False)
    dokumentnummer: Mapped[str] = mapped_column(nullable=False)
    wahlperiode: Mapped[int] = mapped_column(nullable=True)
    herausgeber: Mapped[Herausgeber] = mapped_column(nullable=False)
    datum: Mapped[dt.date] = mapped_column(nullable=False)
    aktualisiert: Mapped[dt.datetime] = mapped_column(nullable=False)
    titel: Mapped[str] = mapped_column(nullable=False)
    autoren_anzahl: Mapped[int] = mapped_column(nullable=False)
    pdf_hash: Mapped[str] = mapped_column(nullable=True)
    vorgangsbezug_anzahl: Mapped[int] = mapped_column(nullable=False)
    anlagen: Mapped[str] = mapped_column(nullable=True)

    autoren: Mapped[list["DIPAutor"]] = relationship(
        cascade='merge, save-update, delete, delete-orphan'
    )

    fundstelle: Mapped["DIPFundstelle"] = relationship(
        cascade='merge, save-update, delete, delete-orphan',
        back_populates="drucksache",
        foreign_keys="DIPFundstelle.drucksache_id",
    )

    urheber: Mapped[list["DIPUrheber"]] = relationship(
        cascade='merge, save-update, delete, delete-orphan',
        foreign_keys="DIPUrheber.drucksache_id",
    )

    vorgangsbezug: Mapped[list["DIPVorgangsbezug"]] = relationship(
        cascade='merge, save-update, delete, delete-orphan'
    )

    ressort: Mapped[list["DIPRessort"]] = relationship(
        cascade='merge, save-update, delete, delete-orphan',
        foreign_keys="DIPRessort.drucksache_id",
    )

    drucksache_text: Mapped["DIPDrucksacheText"] = relationship(
        cascade='merge, save-update, delete, delete-orphan',
        back_populates="drucksache",
    )


class DIPAutor(Base, TimestampMixin, DIPSchema):
    __tablename__ = "autor"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id
    drucksache_id: Mapped[int] = mapped_column(
        ForeignKey(f"{SchemaNames.DEUTSCHER_BUNDESTAG}.drucksache.id"), nullable=False
    )
    titel: Mapped[str] = mapped_column(nullable=False)
    autor_titel: Mapped[str] = mapped_column(nullable=False)


class DIPDrucksacheText(Base, TimestampMixin, DIPSchema):
    __tablename__ = "drucksache_text"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id
    drucksache_id: Mapped[int] = mapped_column(
        ForeignKey(f"{SchemaNames.DEUTSCHER_BUNDESTAG}.drucksache.id"), nullable=False
    )
    text: Mapped[str] = mapped_column(nullable=False)

    drucksache: Mapped["DIPDrucksache"] = relationship(
        "DIPDrucksache", back_populates="drucksache_text"
    )
