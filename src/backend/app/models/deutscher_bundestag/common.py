from backend.app.models.config import SchemaNames
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime


class DIPSchema:
    __table_args__ = {"schema": SchemaNames.DEUTSCHER_BUNDESTAG}


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
