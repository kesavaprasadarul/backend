"""Import all sqlalchemy models to make it discoverable."""
# Import all the models, so that Base has them before being imported by alembic
# (In case we are using alembic later on for versioning our database models)
from backend.app.db.database import Base  # pylint: disable=unused-import
from backend.app.models.example_model import ExampleModel  # pylint: disable=unused-import
from backend.app.models.deutscher_bundestag.drucksache_model import (  # pylint: disable=unused-import
    DIPDrucksache,  # pylint: disable=unused-import
    DIPRessort,  # pylint: disable=unused-import
    DIPUrheber,  # pylint: disable=unused-import
    DIPFundstelle,  # pylint: disable=unused-import
    DIPVorgangsbezug,  # pylint: disable=unused-import
    DIPAutor,  # pylint: disable=unused-import
)  # pylint: disable=unused-import

from backend.app.models.deutscher_bundestag.vorgang_model import (  # pylint: disable=unused-import
    DIPVorgang,  # pylint: disable=unused-import
    DIPInkrafttreten,  # pylint: disable=unused-import
    DIPVerkuendung,  # pylint: disable=unused-import
    DIPVorgangDeskriptor,  # pylint: disable=unused-import
    DIPVorgangVerlinkung,  # pylint: disable=unused-import
)  # pylint: disable=unused-import
