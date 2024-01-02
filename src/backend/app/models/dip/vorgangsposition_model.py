"""Deutscher Bundestag Drucksache SQLAlchemy Models for creating associated tables in database."""
import datetime as dt

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.database import Base
from backend.app.facades.deutscher_bundestag.model import (
    Abstimmungsart,
    Dokumentart,
    Mehrheit,
    VorgangspositionTyp,
    Zuordnung,
)
from backend.app.models.common import DIPSchema, TimestampMixin
from backend.app.models.dip.fundstelle_model import DIPFundstelle
from backend.app.models.dip.ressort_model import DIPRessort
from backend.app.models.dip.urheber_model import DIPUrheber


class DIPVorgangsposition(Base, TimestampMixin, DIPSchema):
    """Table attributes for Model/Relation/Table vorgangsposition."""

    __tablename__ = "vorgangsposition"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id

    vorgangsposition: Mapped[str] = mapped_column(nullable=False)
    zuordnung: Mapped[Zuordnung] = mapped_column(nullable=False)
    gang: Mapped[bool] = mapped_column(nullable=False)
    fortsetzung: Mapped[bool] = mapped_column(nullable=False)
    nachtrag: Mapped[bool] = mapped_column(nullable=False)
    vorgangstyp: Mapped[str] = mapped_column(nullable=False)
    typ: Mapped[VorgangspositionTyp] = mapped_column(nullable=False)
    titel: Mapped[str] = mapped_column(nullable=False)
    dokumentart: Mapped[Dokumentart] = mapped_column(nullable=False)
    vorgang_id: Mapped[int] = mapped_column(nullable=False)
    datum: Mapped[dt.date] = mapped_column(nullable=False)
    aktualisiert: Mapped[dt.datetime] = mapped_column(nullable=True)
    aktivitaet_anzahl: Mapped[int] = mapped_column(nullable=False)
    ratsdok: Mapped[str] = mapped_column(nullable=True)
    kom: Mapped[str] = mapped_column(nullable=True)
    sek: Mapped[str] = mapped_column(nullable=True)
    abstract: Mapped[str] = mapped_column(nullable=True)

    fundstelle: Mapped["DIPFundstelle"] = relationship(
        cascade='merge, save-update, delete, delete-orphan',
        back_populates="vorgangsposition",
        foreign_keys="DIPFundstelle.vorgangsposition_id",
    )

    urheber: Mapped[list["DIPUrheber"]] = relationship(
        cascade='merge, save-update, delete, delete-orphan',
        foreign_keys="DIPUrheber.vorgangsposition_id",
    )

    ueberweisung: Mapped[list["DIPUeberweisung"]] = relationship(
        cascade='merge, save-update, delete, delete-orphan'
    )

    aktivitaet_anzeige: Mapped[list["DIPAktivitaetAnzeige"]] = relationship(
        cascade='merge, save-update, delete, delete-orphan'
    )

    ressort: Mapped[list["DIPRessort"]] = relationship(
        cascade='merge, save-update, delete, delete-orphan',
        foreign_keys="DIPRessort.vorgangsposition_id",
    )

    beschlussfassung: Mapped[list["DIPBeschlussfassung"]] = relationship(
        cascade='merge, save-update, delete, delete-orphan'
    )

    vorgangspositionbezug: Mapped[list["DIPVorgangspositionbezug"]] = relationship(
        cascade='merge, save-update, delete, delete-orphan',
        foreign_keys="DIPVorgangspositionbezug.vorgangsposition_id",
    )


class DIPUeberweisung(Base, TimestampMixin, DIPSchema):
    """Table attributes for Model/Relation/Table ueberweisung."""

    __tablename__ = "ueberweisung"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id
    vorgangsposition_id: Mapped[int] = mapped_column(
        ForeignKey("dip.vorgangsposition.id"), nullable=False
    )

    ausschuss: Mapped[str] = mapped_column(nullable=False)
    ausschuss_kuerzel: Mapped[str] = mapped_column(nullable=False)
    federfuehrung: Mapped[bool] = mapped_column(nullable=False)
    ueberweisungsart: Mapped[str] = mapped_column(nullable=True)


class DIPAktivitaetAnzeige(Base, TimestampMixin, DIPSchema):
    """Table attributes for Model/Relation/Table aktivitaet_anzeige."""

    __tablename__ = "aktivitaet_anzeige"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id
    vorgangsposition_id: Mapped[int] = mapped_column(
        ForeignKey("dip.vorgangsposition.id"), nullable=False
    )
    aktivitaetsart: Mapped[str] = mapped_column(nullable=False)
    titel: Mapped[str] = mapped_column(nullable=False)
    pdf_url: Mapped[str] = mapped_column(nullable=True)
    seite: Mapped[str] = mapped_column(nullable=True)


class DIPBeschlussfassung(Base, TimestampMixin, DIPSchema):
    """Table attributes for Model/Relation/Table beschlussfassung."""

    __tablename__ = "beschlussfassung"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id
    vorgangsposition_id: Mapped[int] = mapped_column(
        ForeignKey("dip.vorgangsposition.id"), nullable=False
    )

    beschlusstenor: Mapped[str] = mapped_column(nullable=False)
    seite: Mapped[str] = mapped_column(nullable=True)
    abstimmungsart: Mapped[Abstimmungsart] = mapped_column(nullable=True)
    abstimm_ergebnis_bemerkung: Mapped[str] = mapped_column(nullable=True)
    grundlage: Mapped[str] = mapped_column(nullable=True)
    dokumentnummer: Mapped[str] = mapped_column(nullable=True)
    mehrheit: Mapped[Mehrheit] = mapped_column(nullable=True)


class DIPVorgangspositionbezug(Base, TimestampMixin, DIPSchema):
    """Table attributes for Model/Relation/Table vorgangspositionbezug."""

    __tablename__ = "vorgangspositionbezug"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id
    vorgangsposition_id: Mapped[int] = mapped_column(
        ForeignKey("dip.vorgangsposition.id"), nullable=False
    )
    from_vorgang_id: Mapped[int] = mapped_column(nullable=False)

    to_vorgang_id: Mapped[int] = mapped_column(nullable=False)

    titel: Mapped[str] = mapped_column(nullable=False)
    vorgangstyp: Mapped[str] = mapped_column(nullable=False)
    vorgangsposition: Mapped[str] = mapped_column(nullable=False)
