from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.database import Base
from backend.app.facades.deutscher_bundestag.model import Rolle
from backend.app.models.common import DIPSchema, TimestampMixin


class DIPUrheber(Base, TimestampMixin, DIPSchema):
    __tablename__ = "urheber"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id
    drucksache_id: Mapped[int] = mapped_column(ForeignKey("dip.drucksache.id"), nullable=True)
    vorgangsposition_id: Mapped[int] = mapped_column(
        ForeignKey("dip.vorgangsposition.id"), nullable=True
    )
    einbringer: Mapped[bool] = mapped_column(nullable=True)
    bezeichnung: Mapped[str] = mapped_column(nullable=False)
    titel: Mapped[str] = mapped_column(nullable=False)
    rolle: Mapped[Rolle] = mapped_column(nullable=True)
