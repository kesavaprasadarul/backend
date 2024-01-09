"""Deutscher Bundestag Drucksache SQLAlchemy Models for creating associated tables in database."""
import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.database import Base
from backend.app.facades.deutscher_bundestag.model import (
    DokumentartPlenarprotokoll,
    DokumentTyp,
    Zuordnung,
)
from backend.app.models.common import DIPSchema, TimestampMixin
from backend.app.models.dip.fundstelle_model import DIPFundstelle
from backend.app.models.dip.vorgang_model import DIPVorgang
from backend.app.models.dip.vorgangsbezug_model import DIPVorgangsbezug


class DIPPlenarprotokoll(Base, DIPSchema, TimestampMixin):
    """Table attributes for Model/Relation/Table plenarprotokoll."""

    __tablename__ = "plenarprotokoll"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id
    dokumentart: Mapped[DokumentartPlenarprotokoll] = mapped_column(nullable=False)
    typ: Mapped[DokumentTyp] = mapped_column(nullable=False)
    dokumentnummer: Mapped[str] = mapped_column(nullable=False)
    wahlperiode: Mapped[int] = mapped_column(nullable=True)
    herausgeber: Mapped[Zuordnung] = mapped_column(nullable=False)
    datum: Mapped[datetime.date] = mapped_column(nullable=False)
    aktualisiert: Mapped[str] = mapped_column(nullable=False)
    titel: Mapped[str] = mapped_column(nullable=False)
    pdf_hash: Mapped[str] = mapped_column(nullable=True)
    vorgangsbezug_anzahl: Mapped[int] = mapped_column(nullable=False)
    sitzungsbemerkung: Mapped[str] = mapped_column(nullable=True)

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

    plenarprotokoll_vorgang_association: Mapped[
        list["DIPPlenarprotokollVorgangAssociation"]
    ] = relationship(
        back_populates="plenarprotokoll",
        cascade='merge, save-update, delete, delete-orphan',
    )

    vorgaenge: AssociationProxy[list["DIPVorgang"]] = association_proxy(
        "plenarprotokoll_vorgang_association",
        "vorgang",
        creator=lambda vorgang: DIPPlenarprotokollVorgangAssociation(vorgang=vorgang),
    )


class DIPPlenarprotokollText(Base, TimestampMixin, DIPSchema):
    __tablename__ = "plenarprotokoll_text"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id
    plenarprotokoll_id: Mapped[int] = mapped_column(
        ForeignKey("dip.plenarprotokoll.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False
    )
    text: Mapped[str] = mapped_column(nullable=False)

    plenarprotokoll: Mapped["DIPPlenarprotokoll"] = relationship(
        "DIPPlenarprotokoll", back_populates="plenarprotokoll_text"
    )


class DIPPlenarprotokollVorgangAssociation(Base, TimestampMixin, DIPSchema):
    __tablename__ = "plenarprotokoll_vorgang_association"

    plenarprotokoll_id: Mapped[int] = mapped_column(
        ForeignKey("dip.plenarprotokoll.id"), primary_key=True
    )
    vorgang_id: Mapped[int] = mapped_column(ForeignKey("dip.vorgang.id"), primary_key=True)

    plenarprotokoll: Mapped["DIPPlenarprotokoll"] = relationship(
        "DIPPlenarprotokoll", back_populates="plenarprotokoll_vorgang_association"
    )
    vorgang: Mapped["DIPVorgang"] = relationship("DIPVorgang", back_populates="plenarprotokolle")
