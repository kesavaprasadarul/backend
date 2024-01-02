"""Deutscher Bundestag Drucksache SQLAlchemy Models for creating associated tables in database."""
import datetime as dt

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.database import Base
from backend.app.models.common import BTSchema, TimestampMixin
from backend.app.facades.bundestag.model import Vote


class BTAbstimmung(Base, TimestampMixin, BTSchema):
    """Table attributes for Model/Relation/Table abstimmung."""

    __tablename__ = "abstimmung"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id

    title: Mapped[str] = mapped_column(nullable=False)

    abstimmung_date: Mapped[dt.date] = mapped_column(nullable=False)

    ja: Mapped[int] = mapped_column(nullable=False)

    nein: Mapped[int] = mapped_column(nullable=False)

    enthalten: Mapped[int] = mapped_column(nullable=False)

    nicht_abgegeben: Mapped[int] = mapped_column(nullable=False)

    dachzeile: Mapped[str] = mapped_column(nullable=True)

    individual_votes: Mapped[list["BTEinzelpersonAbstimmung"]] = relationship(
        back_populates="abstimmung", cascade="merge, save-update, delete, delete-orphan"
    )

    drucksachen: Mapped[list["BTAbstimmungDrucksache"]] = relationship(
        back_populates="abstimmung", cascade="merge, save-update, delete, delete-orphan"
    )

    redner: Mapped[list["BTAbstimmungRedner"]] = relationship(
        back_populates="abstimmung", cascade="merge, save-update, delete, delete-orphan"
    )


class BTEinzelpersonAbstimmung(Base, TimestampMixin, BTSchema):
    """Table attributes for Model/Relation/Table einzelperson_abstimmung."""

    __tablename__ = "einzelperson_abstimmung"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id

    abstimmung_id: Mapped[int] = mapped_column(ForeignKey("bt.abstimmung.id"), nullable=False)

    person_id: Mapped[int] = mapped_column(ForeignKey("bt.person.id"), nullable=False)

    vote: Mapped[Vote] = mapped_column(nullable=False)

    person: Mapped["BTPerson"] = relationship("BTPerson", back_populates="individual_votes")

    abstimmung: Mapped["BTAbstimmung"] = relationship(
        "BTAbstimmung", back_populates="individual_votes"
    )


class BTAbstimmungDrucksache(Base, TimestampMixin, BTSchema):
    """Table attributes for Model/Relation/Table abstimmung_drucksache."""

    __tablename__ = "abstimmung_drucksache"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id

    drucksache_url: Mapped[str] = mapped_column(nullable=False)

    drucksache_name: Mapped[str] = mapped_column(nullable=False)

    abstimmung_id: Mapped[int] = mapped_column(ForeignKey("bt.abstimmung.id"), nullable=False)

    abstimmung: Mapped["BTAbstimmung"] = relationship(
        "BTAbstimmung",
        back_populates="drucksachen",
    )


class BTAbstimmungRedner(Base, TimestampMixin, BTSchema):
    """Table attributes for Model/Relation/Table abstimmung_redner."""

    __tablename__ = "abstimmung_redner"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id

    abstimmung_id: Mapped[int] = mapped_column(ForeignKey("bt.abstimmung.id"), nullable=False)

    function: Mapped[str] = mapped_column(nullable=False)

    bt_video_id: Mapped[str] = mapped_column(nullable=False)

    video_url: Mapped[str] = mapped_column(nullable=False)

    image_url: Mapped[str] = mapped_column(nullable=False)

    abstimmung: Mapped["BTAbstimmung"] = relationship(
        "BTAbstimmung",
        back_populates="redner",
    )


class BTPerson(Base, TimestampMixin, BTSchema):
    """Table attributes for Model/Relation/Table person."""

    __tablename__ = "person"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id

    name: Mapped[str] = mapped_column(nullable=False)

    surname: Mapped[str] = mapped_column(nullable=False)

    title: Mapped[str] = mapped_column(nullable=True)

    fraktion: Mapped[str] = mapped_column(nullable=False)

    bundesland: Mapped[str] = mapped_column(nullable=False)

    biography_url: Mapped[str] = mapped_column(nullable=False)

    image_url: Mapped[str] = mapped_column(nullable=True)

    individual_votes: Mapped[list["BTEinzelpersonAbstimmung"]] = relationship(
        back_populates="person",
    )
