"""Deutscher Bundestag Drucksache SQLAlchemy Models for creating associated tables in database."""
from datetime import date, datetime

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.database import Base
from backend.app.facades.deutscher_bundestag.model import VorgangDeskriptorTyp, VorgangTyp
from backend.app.models.common import DIPSchema, TimestampMixin
from backend.app.models.deutscher_bundestag.vorgangsposition_model import DIPVorgangsposition


class DIPVorgang(Base, TimestampMixin, DIPSchema):
    """Table attributes for Model/Relation/Table drucksache."""

    __tablename__ = "vorgang"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id
    typ: Mapped[VorgangTyp] = mapped_column(nullable=False)
    beratungsstand: Mapped[str] = mapped_column(nullable=True)
    vorgangstyp: Mapped[str] = mapped_column(nullable=False)
    wahlperiode: Mapped[int] = mapped_column(nullable=False)
    initiative: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=True)
    datum: Mapped[date] = mapped_column(nullable=True)
    aktualisiert: Mapped[datetime] = mapped_column(nullable=False)
    titel: Mapped[str] = mapped_column(nullable=False)
    abstract: Mapped[str] = mapped_column(nullable=True)
    sachgebiet: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=True)

    gesta: Mapped[str] = mapped_column(nullable=True)
    zustimmungsbeduerftigkeit: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=True)
    kom: Mapped[str] = mapped_column(nullable=True)
    ratsdok: Mapped[str] = mapped_column(nullable=True)
    archiv: Mapped[str] = mapped_column(nullable=True)
    mitteilung: Mapped[str] = mapped_column(nullable=True)
    sek: Mapped[str] = mapped_column(nullable=True)

    drucksache_id: Mapped[int] = mapped_column(ForeignKey("dip.drucksache.id"), nullable=True)
    plenarprotokoll_id: Mapped[int] = mapped_column(
        ForeignKey("dip.plenarprotokoll.id"), nullable=True
    )

    deskriptor: Mapped[list["DIPVorgangDeskriptor"]] = relationship(
        cascade='merge, save-update, delete, delete-orphan'
    )

    verkuendung: Mapped[list["DIPVerkuendung"]] = relationship(
        cascade='merge, save-update, delete, delete-orphan'
    )

    inkrafttreten: Mapped[list["DIPInkrafttreten"]] = relationship(
        cascade='merge, save-update, delete, delete-orphan'
    )

    vorgang_verlinkung: Mapped[list["DIPVorgangVerlinkung"]] = relationship(
        cascade='merge, save-update, delete, delete-orphan'
    )

    vorgangsposition: Mapped[list["DIPVorgangsposition"]] = relationship(
        cascade='merge, save-update',
        foreign_keys="DIPVorgangsposition.vorgang_id",
        primaryjoin="DIPVorgang.id==DIPVorgangsposition.vorgang_id",
    )


class DIPVorgangDeskriptor(Base, TimestampMixin, DIPSchema):
    """Table attributes for Model/Relation/Table drucksache."""

    __tablename__ = "vorgang_deskriptor"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id
    vorgang_id: Mapped[int] = mapped_column(ForeignKey("dip.vorgang.id"), nullable=False)

    name: Mapped[str] = mapped_column(nullable=False)
    typ: Mapped[VorgangDeskriptorTyp] = mapped_column(nullable=False)
    fundstelle: Mapped[bool] = mapped_column(nullable=False)


class DIPVerkuendung(Base, TimestampMixin, DIPSchema):
    """Table attributes for Model/Relation/Table drucksache."""

    __tablename__ = "verkuendung"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id
    vorgang_id: Mapped[int] = mapped_column(ForeignKey("dip.vorgang.id"), nullable=False)

    jahrgang: Mapped[str] = mapped_column(nullable=True)
    heftnummer: Mapped[str] = mapped_column(nullable=True)
    seite: Mapped[str] = mapped_column(nullable=True)
    ausfertigungsdatum: Mapped[date] = mapped_column(nullable=False)
    verkuendungsdatum: Mapped[date] = mapped_column(nullable=False)
    rubrik_nr: Mapped[str] = mapped_column(nullable=True)
    einleitungstext: Mapped[str] = mapped_column(nullable=True)
    verkuendungsblatt_bezeichnung: Mapped[str] = mapped_column(nullable=True)
    verkuendungsblatt_kuerzel: Mapped[str] = mapped_column(nullable=True)
    fundstelle: Mapped[str] = mapped_column(nullable=False)
    pdf_url: Mapped[str] = mapped_column(nullable=True)
    titel: Mapped[str] = mapped_column(nullable=True)


class DIPInkrafttreten(Base, TimestampMixin, DIPSchema):
    """Table attributes for Model/Relation/Table drucksache."""

    __tablename__ = "inkrafttreten"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id
    vorgang_id: Mapped[int] = mapped_column(ForeignKey("dip.vorgang.id"), nullable=False)

    datum: Mapped[date] = mapped_column(nullable=False)
    erlaeuterung: Mapped[str] = mapped_column(nullable=True)


class DIPVorgangVerlinkung(Base, TimestampMixin, DIPSchema):
    """Table attributes for Model/Relation/Table drucksache."""

    __tablename__ = "vorgang_verlinkung"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id
    vorgang_id: Mapped[int] = mapped_column(ForeignKey("dip.vorgang.id"), nullable=False)

    verweisung: Mapped[str] = mapped_column(nullable=False)
    titel: Mapped[str] = mapped_column(nullable=False)
    wahlperiode: Mapped[int] = mapped_column(nullable=False)
    gesta: Mapped[str] = mapped_column(nullable=True)
