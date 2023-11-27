" Import all models from the deutscher_bundestag app. This is necessary for sqlalchemy to discover them during import. "

# flake8: noqa

from backend.app.models.deutscher_bundestag.drucksache_model import (  # pylint: disable=unused-import
    DIPAutor,
    DIPDrucksacheText,
)
from backend.app.models.deutscher_bundestag.vorgangsposition_model import (  # pylint: disable=unused-import
    DIPVorgangsposition,
    DIPVorgangspositionbezug,
    DIPAktivitaetAnzeige,
    DIPBeschlussfassung,
    DIPUeberweisung,
)
from backend.app.models.deutscher_bundestag.plenarprotokoll_model import (  # pylint: disable=unused-import
    DIPPlenarprotokoll,
    DIPPlenarprotokollText,
)
from backend.app.models.deutscher_bundestag.fundstelle_model import (
    DIPFundstelle,
)  # pylint: disable=unused-import
from backend.app.models.deutscher_bundestag.vorgangsbezug_model import (
    DIPVorgangsbezug,
)  # pylint: disable=unused-import
from backend.app.models.deutscher_bundestag.ressort_model import (
    DIPRessort,
)  # pylint: disable=unused-import
from backend.app.models.deutscher_bundestag.urheber_model import (
    DIPUrheber,
)  # pylint: disable=unused-import
from backend.app.models.deutscher_bundestag.vorgang_model import (  # pylint: disable=unused-import
    DIPVorgang,
    DIPVerkuendung,
    DIPInkrafttreten,
    DIPVorgangDeskriptor,
    DIPVorgangVerlinkung,  #
)
