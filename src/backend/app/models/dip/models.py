" Import all models from the deutscher_bundestag app. This is necessary for sqlalchemy to discover them during import. "

# flake8: noqa

from backend.app.models.dip.drucksache_model import (  # pylint: disable=unused-import
    DIPAutor,
    DIPDrucksache,
    DIPDrucksacheText,
    DIPDrucksacheVorgangAssociation,
)
from backend.app.models.dip.fundstelle_model import (  # pylint: disable=unused-import
    DIPFundstelle,
)
from backend.app.models.dip.plenarprotokoll_model import (  # pylint: disable=unused-import
    DIPPlenarprotokoll,
    DIPPlenarprotokollText,
    DIPPlenarprotokollVorgangAssociation,
)
from backend.app.models.dip.ressort_model import (  # pylint: disable=unused-import
    DIPRessort,
)
from backend.app.models.dip.urheber_model import (  # pylint: disable=unused-import
    DIPUrheber,
)
from backend.app.models.dip.vorgang_model import (  # pylint: disable=unused-import
    DIPInkrafttreten,
    DIPVerkuendung,
    DIPVorgang,
    DIPVorgangDeskriptor,
    DIPVorgangVerlinkung,
)
from backend.app.models.dip.vorgangsbezug_model import (  # pylint: disable=unused-import
    DIPVorgangsbezug,
)
from backend.app.models.dip.vorgangsposition_model import (  # pylint: disable=unused-import
    DIPAktivitaetAnzeige,
    DIPBeschlussfassung,
    DIPUeberweisung,
    DIPVorgangsposition,
    DIPVorgangspositionbezug,
)
