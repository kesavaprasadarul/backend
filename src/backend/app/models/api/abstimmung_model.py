from datetime import date, datetime

from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.database import Base
from backend.app.models.common import APISchema, TimestampMixin


class APIAbstimmung(Base, TimestampMixin):
    """Table attributes for Model/Relation/Table example_model."""

    __tablename__ = "abstimmung"
    id: Mapped[int] = mapped_column(primary_key=True)  # database id

    titel: Mapped[str] = mapped_column(nullable=False)
    abstimmung_datum: Mapped[date] = mapped_column(nullable=False)
    akzeptiert: Mapped[bool] = mapped_column(nullable=False)
    ja: Mapped[int] = mapped_column(nullable=False)
    nein: Mapped[int] = mapped_column(nullable=False)
    enthalten: Mapped[int] = mapped_column(nullable=False)
    nicht_abgegeben: Mapped[int] = mapped_column(nullable=False)
    aktualisiert: Mapped[datetime] = mapped_column(nullable=False)
