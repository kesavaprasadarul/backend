from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from backend.app.db.database import Base
from backend.app.models.config import SchemaNames
from backend.app.models.deutscher_bundestag.common import DIPSchema, TimestampMixin


class DIPRessort(Base, TimestampMixin, DIPSchema):
    __tablename__ = "ressort"

    id: Mapped[int] = mapped_column(primary_key=True)  # database id
    drucksache_id: Mapped[int] = mapped_column(
        ForeignKey(f"{SchemaNames.DEUTSCHER_BUNDESTAG}.drucksache.id"), nullable=True
    )

    vorgangsposition_id: Mapped[int] = mapped_column(
        ForeignKey(f"{SchemaNames.DEUTSCHER_BUNDESTAG}.vorgangsposition.id"),
        nullable=True,
    )

    federfuehrend: Mapped[bool] = mapped_column(nullable=False)
    titel: Mapped[str] = mapped_column(nullable=False)
