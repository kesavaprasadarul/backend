"""Import all sqlalchemy models to make it discoverable."""
# Import all the models, so that Base has them before being imported by alembic
# (In case we are using alembic later on for versioning our database models)

# flake8: noqa
from backend.app.db.database import Base  # pylint: disable=unused-import
from backend.app.models.api.abstimmung_model import APIAbstimmung
from backend.app.models.api.mandate_model import APIMandate
from backend.app.models.api.top_topics_model import TopTopics  # pylint: disable=unused-import
from backend.app.models.bundestag.abstimmung_model import (  # pylint: disable=unused-import
    BTAbstimmung,
    BTAbstimmungDrucksache,
    BTAbstimmungRedner,
    BTEinzelpersonAbstimmung,
    BTPerson,
)
from backend.app.models.dip.drucksache_model import DIPAutor  # pylint: disable=unused-import
from backend.app.models.dip.drucksache_model import DIPDrucksache  # pylint: disable=unused-import
from backend.app.models.dip.drucksache_model import (
    DIPVorgangsbezug,  # pylint: disable=unused-import; pylint: disable=unused-import
)
from backend.app.models.dip.drucksache_model import DIPDrucksacheText
from backend.app.models.dip.fundstelle_model import DIPFundstelle  # pylint: disable=unused-import
from backend.app.models.dip.plenarprotokoll_model import (  # pylint: disable=unused-import
    DIPPlenarprotokoll,
    DIPPlenarprotokollText,
)
from backend.app.models.dip.ressort_model import DIPRessort  # pylint: disable=unused-import
from backend.app.models.dip.urheber_model import DIPUrheber  # pylint: disable=unused-import
from backend.app.models.dip.vorgang_model import DIPInkrafttreten  # pylint: disable=unused-import
from backend.app.models.dip.vorgang_model import DIPVerkuendung  # pylint: disable=unused-import
from backend.app.models.dip.vorgang_model import DIPVorgang  # pylint: disable=unused-import
from backend.app.models.dip.vorgang_model import (
    DIPVorgangDeskriptor,  # pylint: disable=unused-import
)
from backend.app.models.dip.vorgang_model import (
    DIPVorgangVerlinkung,  # pylint: disable=unused-import; pylint: disable=unused-import
)
from backend.app.models.dip.vorgangsposition_model import (  # pylint: disable=unused-import
    DIPAktivitaetAnzeige,
    DIPBeschlussfassung,
    DIPUeberweisung,
    DIPVorgangsposition,
    DIPVorgangspositionbezug,
)
from backend.app.models.example_model import ExampleModel  # pylint: disable=unused-import
