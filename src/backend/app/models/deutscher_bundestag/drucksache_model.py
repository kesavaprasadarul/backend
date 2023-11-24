"""Deutscher Bundestag Drucksache SQLAlchemy Models for creating associated tables in database."""
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ARRAY
from backend.app.db.database import Base
from backend.app.models.config import SchemaNames
from backend.app.facades.deutscher_bundestag.model import (
    DokumentTyp,
    DokumentartDrucksache,
    Herausgeber,
    Dokumentart,
    Zuordnung,
    Quadrant,
    Rolle,
)
from datetime import date, datetime


class DIPSchema:
    __table_args__ = {"schema": SchemaNames.DEUTSCHER_BUNDESTAG}


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())


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
    date: Mapped[str] = mapped_column(nullable=True)
    datum: Mapped[str] = mapped_column(nullable=False)
    aktualisiert: Mapped[str] = mapped_column(nullable=False)
    titel: Mapped[str] = mapped_column(nullable=False)
    autoren_anzahl: Mapped[int] = mapped_column(nullable=False)
    pdf_hash: Mapped[str] = mapped_column(nullable=True)
    vorgangsbezug_anzahl: Mapped[int] = mapped_column(nullable=False)
    anlagen: Mapped[str] = mapped_column(nullable=True)

    autoren: Mapped[list["DIPAutor"]] = relationship(
        cascade='merge, save-update, delete, delete-orphan'
    )

    fundstelle: Mapped["DIPFundstelle"] = relationship(
        cascade='merge, save-update, delete, delete-orphan'
    )

    urheber: Mapped[list["DIPUrheber"]] = relationship(
        cascade='merge, save-update, delete, delete-orphan'
    )

    vorgangsbezug: Mapped[list["DIPVorgangsbezug"]] = relationship(
        cascade='merge, save-update, delete, delete-orphan'
    )

    ressort: Mapped[list["DIPRessort"]] = relationship(
        cascade='merge, save-update, delete, delete-orphan'
    )


class DIPRessort(Base, TimestampMixin, DIPSchema):
    __tablename__ = "ressort"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id
    drucksache_id: Mapped[int] = mapped_column(
        ForeignKey(f"{SchemaNames.DEUTSCHER_BUNDESTAG}.drucksache.id"), nullable=False
    )
    federfuehrend: Mapped[bool] = mapped_column(nullable=False)
    titel: Mapped[str] = mapped_column(nullable=False)


class DIPVorgangsbezug(Base, TimestampMixin, DIPSchema):
    __tablename__ = "vorgangsbezug"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id
    drucksache_id: Mapped[int] = mapped_column(
        ForeignKey(f"{SchemaNames.DEUTSCHER_BUNDESTAG}.drucksache.id"), nullable=False
    )

    titel: Mapped[str] = mapped_column(nullable=False)
    vorgangstyp: Mapped[str] = mapped_column(nullable=False)


class DIPUrheber(Base, TimestampMixin, DIPSchema):
    __tablename__ = "urheber"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id
    drucksache_id: Mapped[int] = mapped_column(
        ForeignKey(f"{SchemaNames.DEUTSCHER_BUNDESTAG}.drucksache.id"), nullable=False
    )
    einbringer: Mapped[bool] = mapped_column(nullable=True)
    bezeichnung: Mapped[str] = mapped_column(nullable=False)
    titel: Mapped[str] = mapped_column(nullable=False)
    rolle: Mapped[Rolle] = mapped_column(nullable=True)


class DIPFundstelle(Base, TimestampMixin, DIPSchema):
    __tablename__ = "fundstelle"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id

    drucksache_id: Mapped[int] = mapped_column(
        ForeignKey(f"{SchemaNames.DEUTSCHER_BUNDESTAG}.drucksache.id"), nullable=False
    )

    dokumentart: Mapped[Dokumentart] = mapped_column(nullable=False)
    pdf_url: Mapped[str] = mapped_column(nullable=True)
    dokumentnummer: Mapped[str] = mapped_column(nullable=False)
    datum: Mapped[date] = mapped_column(nullable=False)
    drucksachetyp: Mapped[str] = mapped_column(nullable=True)
    herausgeber: Mapped[Zuordnung] = mapped_column(nullable=False)
    urheber: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)
    verteildatum: Mapped[datetime] = mapped_column(nullable=True)
    seite: Mapped[str] = mapped_column(nullable=True)
    anfangsseite: Mapped[int] = mapped_column(nullable=True)
    endseite: Mapped[int] = mapped_column(nullable=True)
    anfangsquadrant: Mapped[Quadrant] = mapped_column(nullable=True)
    endquadrant: Mapped[Quadrant] = mapped_column(nullable=True)
    frage_nummer: Mapped[str] = mapped_column(nullable=True)
    anlagen: Mapped[str] = mapped_column(nullable=True)
    top: Mapped[int] = mapped_column(nullable=True)
    top_zusatz: Mapped[str] = mapped_column(nullable=True)

    drucksache: Mapped["DIPDrucksache"] = relationship(
        back_populates="fundstelle", single_parent=True
    )


class DIPAutor(Base, TimestampMixin, DIPSchema):
    __tablename__ = "autor"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id
    drucksache_id: Mapped[int] = mapped_column(
        ForeignKey(f"{SchemaNames.DEUTSCHER_BUNDESTAG}.drucksache.id"), nullable=False
    )
    titel: Mapped[str] = mapped_column(nullable=False)
    autor_titel: Mapped[str] = mapped_column(nullable=False)
