from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import Enum, ForeignKey, String

from backend.app.db.database import Base
from datetime import date, datetime
from typing import List
from enum import Enum


class VorgangModel(Base):
    """Table attributes for Model/Relation/Table vorgang."""

    __tablename__ = "vorgang"
    id: Mapped[int] = mapped_column(primary_key=True)  # database id
    typ: Mapped[str] = mapped_column(nullable=False)
    beratungsstand: Mapped[str] = mapped_column(nullable=True)
    vorgangstyp: Mapped[str] = mapped_column(nullable=False)
    wahlperiode: Mapped[str] = mapped_column(nullable=True)
    initiative: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=True)
    datum: Mapped[date] = mapped_column(nullable=True)
    aktualisiert: Mapped[datetime] = mapped_column(nullable=False)
    titel: Mapped[str] = mapped_column(nullable=False)
    abstract: Mapped[str] = mapped_column(nullable=True)
    sachgebiet: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=True)
    gesta: Mapped[str] = mapped_column(nullable=True)
    zustimmungsbeduerftigkeit: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=True)
    kom: Mapped[str] = mapped_column(nullable=True)
    ratsdok: Mapped[str] = mapped_column(nullable=True)
    # verkuendung_id: Mapped[int] = mapped_column(nullable=True)
    inkrafttreten_datum: Mapped[str] = mapped_column(nullable=True)
    inkrafttreten_erlaeuterung: Mapped[str] = mapped_column(nullable=True)
    archiv: Mapped[str] = mapped_column(nullable=True)
    # vorgang_verlinkung_id: Mapped[list[int]] = mapped_column(nullable=True)
    sek: Mapped[str] = mapped_column(nullable=True)

    deskriptor: Mapped[List["VorgangDeskriptorModel"]] = relationship()


class VorgangDeskriptorTyp(Enum):
    FREIER_DESKRIPTOR = "Freier Deskriptor"
    GEOGRAPH = "Geograph"
    BEGRIFFE = "Begriffe"
    INSTITUTIONEN = "Institutionen"
    PERSONEN = "Personen"
    RECHTSMATERIALIEN = "Rechtsmaterialien"
    SACHBEGRIFFE = "Sachbegriffe"


class VorgangDeskriptorModel(Base):
    """Table attributes for Model/Relation/Table vorgang_deskriptor."""

    __tablename__ = "vorgang_deskriptor"
    id: Mapped[int] = mapped_column(primary_key=True)  # database id
    vorgang_id: Mapped[int] = mapped_column(ForeignKey("vorgang.id"), nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    typ: Mapped[VorgangDeskriptorTyp] = mapped_column(nullable=False)
    fundstelle: Mapped[bool] = mapped_column(nullable=False)
