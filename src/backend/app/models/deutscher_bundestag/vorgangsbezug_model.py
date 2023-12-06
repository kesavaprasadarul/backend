from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.database import Base
from backend.app.models.common import DIPSchema, TimestampMixin


class DIPVorgangsbezug(Base, TimestampMixin, DIPSchema):
    __tablename__ = "vorgangsbezug"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id

    vorgang_id: Mapped[int] = mapped_column(nullable=False)

    drucksache_id: Mapped[int] = mapped_column(ForeignKey(f"dip.drucksache.id"), nullable=True)

    plenarprotokoll_id: Mapped[int] = mapped_column(
        ForeignKey(f"dip.plenarprotokoll.id"), nullable=True
    )

    titel: Mapped[str] = mapped_column(nullable=False)
    vorgangstyp: Mapped[str] = mapped_column(nullable=False)
