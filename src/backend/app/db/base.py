"""Import all sqlalchemy models to make it discoverable."""
# Import all the models, so that Base has them before being imported by alembic
# (In case we are using alembic later on for versioning our database models)

# flake8: noqa
from backend.app.db.database import Base  # pylint: disable=unused-import
from backend.app.models.deutscher_bundestag.drucksache_model import (
    DIPAutor,  # pylint: disable=unused-import
)
from backend.app.models.deutscher_bundestag.drucksache_model import (
    DIPDrucksache,  # pylint: disable=unused-import
)
from backend.app.models.deutscher_bundestag.drucksache_model import (
    DIPVorgangsbezug,  # pylint: disable=unused-import; pylint: disable=unused-import
)
from backend.app.models.deutscher_bundestag.drucksache_model import DIPDrucksacheText
from backend.app.models.deutscher_bundestag.fundstelle_model import (  # pylint: disable=unused-import
    DIPFundstelle,
)
from backend.app.models.deutscher_bundestag.plenarprotokoll_model import (  # pylint: disable=unused-import
    DIPPlenarprotokoll,
    DIPPlenarprotokollText,
)
from backend.app.models.deutscher_bundestag.ressort_model import (  # pylint: disable=unused-import
    DIPRessort,
)
from backend.app.models.deutscher_bundestag.urheber_model import (  # pylint: disable=unused-import
    DIPUrheber,
)
from backend.app.models.deutscher_bundestag.vorgang_model import (
    DIPInkrafttreten,  # pylint: disable=unused-import
)
from backend.app.models.deutscher_bundestag.vorgang_model import (
    DIPVerkuendung,  # pylint: disable=unused-import
)
from backend.app.models.deutscher_bundestag.vorgang_model import (
    DIPVorgang,  # pylint: disable=unused-import
)
from backend.app.models.deutscher_bundestag.vorgang_model import (
    DIPVorgangDeskriptor,  # pylint: disable=unused-import
)
from backend.app.models.deutscher_bundestag.vorgang_model import (
    DIPVorgangVerlinkung,  # pylint: disable=unused-import; pylint: disable=unused-import
)
from backend.app.models.deutscher_bundestag.vorgangsposition_model import (  # pylint: disable=unused-import
    DIPAktivitaetAnzeige,
    DIPBeschlussfassung,
    DIPUeberweisung,
    DIPVorgangsposition,
    DIPVorgangspositionbezug,
)
from backend.app.models.example_model import ExampleModel  # pylint: disable=unused-import
