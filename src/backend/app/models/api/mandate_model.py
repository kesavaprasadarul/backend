from datetime import date, datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from sqlalchemy.sql.sqltypes import Text
from sqlalchemy.dialects.postgresql import ARRAY

from backend.app.db.database import Base
from backend.app.models.common import APISchema, TimestampMixin

from backend.app.models.deutscher_bundestag.models import DIPBeschlussfassung, DIPVorgangsposition


class APIMandate(Base, TimestampMixin):
    """Table attributes for Model/Relation/Table mandate."""

    __tablename__ = "mandate"
    id: Mapped[int] = mapped_column(primary_key=True)  # database id

    wahlperiode: Mapped[int] = mapped_column(nullable=False)
    anzahl_stimmberechtigt: Mapped[int] = mapped_column(nullable=False)
    date_from: Mapped[date] = mapped_column(nullable=False)
    date_to: Mapped[date] = mapped_column(nullable=True)
    comment: Mapped[str] = mapped_column(nullable=True)
