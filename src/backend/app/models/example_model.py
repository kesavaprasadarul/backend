"""Example SQLAlchemy Models for creating associated tables in database."""
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.database import Base


class ExampleModel(Base):
    """Table attributes for Model/Relation/Table example_model."""

    __tablename__ = "example_model"
    id: Mapped[int] = mapped_column(primary_key=True)  # database id
    name: Mapped[str] = mapped_column(nullable=True)
