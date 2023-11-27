" Import all models from the deutscher_bundestag app. This is necessary for sqlalchemy to discover them during import. "

# flake8: noqa

from backend.app.models.deutscher_bundestag.drucksache_model import (  # pylint: disable=unused-import
    DIPAutor,
    DIPDrucksache,
    DIPDrucksacheText,
)
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
from backend.app.models.deutscher_bundestag.vorgang_model import (  # pylint: disable=unused-import
    DIPInkrafttreten,
    DIPVerkuendung,
    DIPVorgang,
    DIPVorgangDeskriptor,
    DIPVorgangVerlinkung,
)
from backend.app.models.deutscher_bundestag.vorgangsbezug_model import (  # pylint: disable=unused-import
    DIPVorgangsbezug,
)
from backend.app.models.deutscher_bundestag.vorgangsposition_model import (  # pylint: disable=unused-import
    DIPAktivitaetAnzeige,
    DIPBeschlussfassung,
    DIPUeberweisung,
    DIPVorgangsposition,
    DIPVorgangspositionbezug,
)
