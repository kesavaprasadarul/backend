"""Deutscher Bundestag Drucksache SQLAlchemy Models for creating associated tables in database."""
import datetime as dt

from sqlalchemy import ForeignKey, Sequence
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, Session, mapped_column, object_session, relationship, validates

from backend.app.db.database import Base
from backend.app.facades.bundestag.model import Vote
from backend.app.models.common import BTSchema, TimestampMixin


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

    person: Mapped["BTPerson"] = relationship(
        "BTPerson",
        back_populates="individual_votes",
        cascade="merge, save-update",
    )

    abstimmung: Mapped["BTAbstimmung"] = relationship(
        "BTAbstimmung",
        back_populates="individual_votes",
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

    id: Mapped[int] = mapped_column(
        Sequence('abstimmung_redner_id_seq', schema='bt'), unique=True, nullable=False
    )  # database id

    abstimmung_id: Mapped[int] = mapped_column(
        ForeignKey("bt.abstimmung.id"), nullable=False, primary_key=True
    )

    name: Mapped[str] = mapped_column(nullable=False, primary_key=True)

    surname: Mapped[str] = mapped_column(nullable=False, primary_key=True)

    function: Mapped[str] = mapped_column(nullable=False, primary_key=True)

    title: Mapped[str] = mapped_column(nullable=True)

    image_url: Mapped[str] = mapped_column(nullable=False)

    abstimmung: Mapped["BTAbstimmung"] = relationship(
        "BTAbstimmung",
        back_populates="redner",
    )

    reden: Mapped[list["BTRede"]] = relationship(
        "BTRede",
        back_populates="abstimmung_redner",
        cascade="merge, save-update, delete, delete-orphan",
    )


class BTRede(Base, TimestampMixin, BTSchema):
    """Table attributes for Model/Relation/Table rede."""

    __tablename__ = "rede"

    id: Mapped[int] = mapped_column(
        Sequence('rede_id_seq', schema='bt'), unique=True, nullable=False
    )  # database id

    abstimmung_redner_id: Mapped[int] = mapped_column(
        ForeignKey("bt.abstimmung_redner.id"), nullable=False
    )

    bt_video_id: Mapped[str] = mapped_column(nullable=False, primary_key=True)

    video_url: Mapped[str] = mapped_column(nullable=False)

    text: Mapped[str] = mapped_column(nullable=True)

    abstimmung_redner: Mapped["BTAbstimmungRedner"] = relationship(
        "BTAbstimmungRedner",
        back_populates="reden",
    )


class BTPerson(Base, TimestampMixin, BTSchema):
    """Table attributes for Model/Relation/Table person."""

    __tablename__ = "person"

    id: Mapped[int] = mapped_column(
        Sequence('person_id_seq', schema='bt'), unique=True, nullable=False
    )  # database id

    biography_url: Mapped[str] = mapped_column(nullable=False, primary_key=True)

    name: Mapped[str] = mapped_column(nullable=False)

    surname: Mapped[str] = mapped_column(nullable=False)

    title: Mapped[str] = mapped_column(nullable=True)

    fraktion: Mapped[str] = mapped_column(nullable=False)

    bundesland: Mapped[str] = mapped_column(nullable=False)

    image_url: Mapped[str] = mapped_column(nullable=True)

    individual_votes: Mapped[list["BTEinzelpersonAbstimmung"]] = relationship(
        back_populates="person",
    )
