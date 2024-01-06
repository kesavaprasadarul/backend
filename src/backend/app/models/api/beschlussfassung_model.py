from datetime import date, datetime

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Text

from backend.app.db.database import Base
from backend.app.models.common import APISchema, TimestampMixin
from backend.app.models.dip.models import DIPBeschlussfassung, DIPVorgangsposition


class APIBeschlussfassung(Base, TimestampMixin):
    """Table attributes for Model/Relation/Table example_model."""

    __tablename__ = "beschlussfassung"
    id: Mapped[int] = mapped_column(primary_key=True)  # database id

    titel: Mapped[str] = mapped_column(nullable=False)
    abstract: Mapped[str] = mapped_column(nullable=True)
    sachgebiet: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=True)

    abstimmung_datum: Mapped[date] = mapped_column(nullable=False)
    abstimmungsart: Mapped[str] = mapped_column(nullable=True)

    akzeptiert: Mapped[bool] = mapped_column(nullable=False)
    ja: Mapped[int] = mapped_column(nullable=False)
    nein: Mapped[int] = mapped_column(nullable=False)
    enthalten: Mapped[int] = mapped_column(nullable=False)
    nicht_abgegeben: Mapped[int] = mapped_column(nullable=False)
    ergebnis_anmerkung: Mapped[str] = mapped_column(nullable=True)

    aktualisiert: Mapped[datetime] = mapped_column(nullable=True)
    initiative: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=True)

    beschlussfassung_id: Mapped[int] = mapped_column(
        ForeignKey("dip.beschlussfassung.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    dip_vorgangsposition_id: Mapped[int] = mapped_column(
        ForeignKey("dip.vorgangsposition.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )

    dip_beschlussfassung: Mapped["DIPBeschlussfassung"] = relationship("DIPBeschlussfassung")
    dip_vorgangsposition: Mapped["DIPVorgangsposition"] = relationship("DIPVorgangsposition")
