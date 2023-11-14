"""Import all sqlalchemy models to make it discoverable."""
# Import all the models, so that Base has them before being imported by alembic
# (In case we are using alembic later on for versioning our database models)
from backend.app.db.database import Base  # pylint: disable=unused-import
from backend.app.models.example_model import ExampleModel  # pylint: disable=unused-import
from backend.app.importer.facades.bundestag_dip.vorgang_model import VorgangModel, VorgangDeskriptorModel  # pylint: disable=unused-import
