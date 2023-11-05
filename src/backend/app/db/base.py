"""Import all sqlalchemy models to make it discoverable."""
# Import all the models, so that Base has them before being imported by alembic
# (In case we are using alembic later on for versioning our database models)
from backend.app.db.database import Base  # pylint: disable
