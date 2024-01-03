from datetime import date, datetime

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Text

from backend.app.db.database import Base
from backend.app.models.common import APISchema, TimestampMixin
from backend.app.models.dip.models import DIPBeschlussfassung, DIPVorgangsposition


class APIMandate(Base, TimestampMixin):
    """Table attributes for Model/Relation/Table mandate."""

    __tablename__ = "mandate"
    id: Mapped[int] = mapped_column(primary_key=True)  # database id

    wahlperiode: Mapped[int] = mapped_column(nullable=False)
    anzahl_stimmberechtigt: Mapped[int] = mapped_column(nullable=False)
    date_from: Mapped[date] = mapped_column(nullable=False)
    date_to: Mapped[date] = mapped_column(nullable=True)
    comment: Mapped[str] = mapped_column(nullable=True)
