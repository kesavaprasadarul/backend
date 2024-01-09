from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column


class APISchema:
    __table_args__ = {"schema": "public"}


class DIPSchema:
    __table_args__ = {"schema": "dip"}


class BTSchema:
    __table_args__ = {"schema": "bt"}


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )
