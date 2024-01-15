"""CRUDBase class with basic CRUD Operations."""
import logging
from typing import Any, Generic, TypeVar

from psycopg2 import IntegrityError
from sqlalchemy import delete, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from backend.app.db.database import Base, SessionLocal

_logger = logging.getLogger(__name__)


ModelType = TypeVar("ModelType", bound=Base)  # pylint: disable=invalid-name


class CRUDBase(Generic[ModelType]):
    """Containing basic CRUD Operations for each table."""

    db: Session = SessionLocal()

    def __init__(self, model: type[ModelType]):
        """
        Init with model object.
        """
        self.model = model

    def create_or_update(self, obj_in: ModelType) -> ModelType:
        """Create single object and add to database."""
        try:
            assert obj_in not in self.db
            CRUDBase.db.merge(obj_in)
            CRUDBase.db.commit()
        except IntegrityError as error:
            CRUDBase.db.flush()
            CRUDBase.db.rollback()
            _logger.error("Inserting or updating entries failed. Error %s occured.", error)
        except OperationalError as error:
            # if database closed unexpectedly, OperationalError occurs
            _logger.error("%s occured. Session will be rolled back.", error)
            CRUDBase.db.rollback()
            CRUDBase.db.merge(obj_in)
            CRUDBase.db.commit()
        return obj_in

    def upsert_many(
        self, obj_in_list: list[ModelType]
    ):  # pylint: disable=redefined-builtin,invalid-name
        """Delete multiple objects in database."""
        try:
            ids = [obj_in.id for obj_in in obj_in_list]
            for id in ids:
                container = CRUDBase.db.get(self.model, id)
                if container:
                    CRUDBase.db.delete(container)
            for obj_in in obj_in_list:
                CRUDBase.db.merge(obj_in)
            CRUDBase.db.commit()
        except OperationalError as error:
            # if database closed unexpectedly, OperationalError occurs
            _logger.error("%s occured. Session will be rolled back.", error)
            CRUDBase.db.rollback()
            CRUDBase.db.execute(delete(self.model).where(self.model.id == id))
            CRUDBase.db.commit()

    def create_or_update_multi(self, obj_in_list: list[ModelType]) -> list[ModelType] | None:
        """Create mutliple objects and add to database."""
        try:
            for obj_in in obj_in_list:
                assert obj_in not in self.db
                CRUDBase.db.merge(obj_in)
            CRUDBase.db.commit()
        except IntegrityError as error:
            CRUDBase.db.flush()
            CRUDBase.db.rollback()
            _logger.error("Inserting or updating entries failed. Error %s occured.", error)
            return None
        except OperationalError as error:
            # if database closed unexpectedly, OperationalError occurs
            _logger.error("%s occured. Session will be rolled back.", error)
            CRUDBase.db.rollback()
            for obj_in in obj_in_list:
                CRUDBase.db.merge(obj_in)
            CRUDBase.db.commit()
        return obj_in_list

    def delete(self, id: Any):  # pylint: disable=redefined-builtin,invalid-name
        """Delete single object in database."""
        try:
            CRUDBase.db.execute(delete(self.model).where(self.model.id == id))
            CRUDBase.db.commit()
        except OperationalError as error:
            # if database closed unexpectedly, OperationalError occurs
            _logger.error("%s occured. Session will be rolled back.", error)
            CRUDBase.db.rollback()
            CRUDBase.db.execute(delete(self.model).where(self.model.id == id))
            CRUDBase.db.commit()

    def delete_all(self):
        """Delete all objects of database table."""
        try:
            CRUDBase.db.execute(delete(self.model))
            CRUDBase.db.commit()
        except OperationalError as error:
            # if database closed unexpectedly, OperationalError occurs
            _logger.error("%s occured. Session will be rolled back.", error)
            CRUDBase.db.rollback()
            CRUDBase.db.execute(delete(self.model))
            CRUDBase.db.commit()

    def read(self, id: Any):  # pylint: disable=redefined-builtin,invalid-name
        """Read single object from database."""
        try:
            return CRUDBase.db.scalar(select(self.model).where(self.model.id == id))
        except OperationalError as error:
            # if database closed unexpectedly, OperationalError occurs
            _logger.error("%s occured. Session will be rolled back.", error)
            CRUDBase.db.rollback()
            return CRUDBase.db.scalar(select(self.model).where(self.model.id == id))

    def read_all(self):
        """Read all objects from database via select."""
        try:
            return CRUDBase.db.scalars(select(self.model)).all()
        except OperationalError as error:
            # if database closed unexpectedly, OperationalError occurs
            _logger.error("%s occured. Session will be rolled back.", error)
            CRUDBase.db.rollback()
            return CRUDBase.db.scalars(select(self.model)).all()

    def read_multi(self, filters: list = [], skip: int = 0, limit: int = 100):
        """Read multi objects from database."""
        try:
            return CRUDBase.db.scalars(
                select(self.model)
                .filter(*filters)
                .order_by(self.model.id)
                .offset(skip)
                .limit(limit)
            ).all()
        except OperationalError as error:
            # if database closed unexpectedly, OperationalError occurs
            _logger.error("%s occured. Session will be rolled back.", error)
            CRUDBase.db.rollback()
            return CRUDBase.db.scalars(
                select(self.model)
                .filter(*filters)
                .order_by(self.model.id)
                .offset(skip)
                .limit(limit)
            ).all()

    def count(self, filters: list = []) -> int:
        """Count objects from database."""
        try:
            return CRUDBase.db.query(self.model).filter(*filters).count()
        except OperationalError as error:
            # if database closed unexpectedly, OperationalError occurs
            _logger.error("%s occured. Session will be rolled back.", error)
            CRUDBase.db.rollback()
            return CRUDBase.db.query(self.model).filter(*filters).count()
