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
from backend.app.models.common import DIPSchema, TimestampMixin
from backend.app.models.dip.fundstelle_model import DIPFundstelle
from backend.app.models.dip.ressort_model import DIPRessort
from backend.app.models.dip.urheber_model import DIPUrheber
from backend.app.models.dip.vorgang_model import DIPVorgang
from backend.app.models.dip.vorgangsbezug_model import DIPVorgangsbezug
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.associationproxy import AssociationProxy


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

    drucksache_vorgang_association: Mapped[list["DIPDrucksacheVorgangAssociation"]] = relationship(
        back_populates="drucksache",
        cascade='merge, save-update, delete, delete-orphan',
    )

    vorgaenge: AssociationProxy[list["DIPVorgang"]] = association_proxy(
        "drucksache_vorgang_association",
        "vorgang",
        creator=lambda vorgang: DIPDrucksacheVorgangAssociation(vorgang=vorgang),
    )


class DIPAutor(Base, TimestampMixin, DIPSchema):
    __tablename__ = "autor"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id
    drucksache_id: Mapped[int] = mapped_column(ForeignKey("dip.drucksache.id"), nullable=False)
    titel: Mapped[str] = mapped_column(nullable=False)
    autor_titel: Mapped[str] = mapped_column(nullable=False)


class DIPDrucksacheText(Base, TimestampMixin, DIPSchema):
    __tablename__ = "drucksache_text"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id
    drucksache_id: Mapped[int] = mapped_column(ForeignKey("dip.drucksache.id"), nullable=False)
    text: Mapped[str] = mapped_column(nullable=False)

    drucksache: Mapped["DIPDrucksache"] = relationship(
        "DIPDrucksache", back_populates="drucksache_text"
    )


class DIPDrucksacheVorgangAssociation(Base, TimestampMixin, DIPSchema):
    __tablename__ = "drucksache_vorgang_association"

    drucksache_id: Mapped[int] = mapped_column(ForeignKey("dip.drucksache.id"), primary_key=True)
    vorgang_id: Mapped[int] = mapped_column(ForeignKey("dip.vorgang.id"), primary_key=True)

    drucksache: Mapped["DIPDrucksache"] = relationship(
        "DIPDrucksache", back_populates="drucksache_vorgang_association"
    )
    vorgang: Mapped["DIPVorgang"] = relationship("DIPVorgang", back_populates="drucksachen")
