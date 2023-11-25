from backend.app.crud.CRUDDIPBundestag.crud_drucksache import CRUD_DIP_DRUCKSACHE
from backend.app.crud.CRUDDIPBundestag.crud_vorgang import CRUD_DIP_VORGANG
from backend.app.facades.deutscher_bundestag.facade import DIPBundestagFacade
from backend.app.facades.facade import (
    Auth,
    AuthType,
)
from backend.app.core.config import settings

from backend.app.facades.deutscher_bundestag.model import Drucksache, Vorgang
from backend.app.models.deutscher_bundestag.drucksache_model import (
    DIPDrucksache,
    DIPRessort,
    DIPUrheber,
    DIPFundstelle,
    DIPVorgangsbezug,
    DIPAutor,
)

from backend.app.models.deutscher_bundestag.vorgang_model import (
    DIPVorgang,
    DIPInkrafttreten,
    DIPVerkuendung,
    DIPVorgangDeskriptor,
    DIPVorgangVerlinkung,
)

from backend.app.models.deutscher_bundestag.vorgangsposition_model import (
    DIPVorgangsposition,
)


def import_drucksache(drucksache: Drucksache):
    dip_autoren = (
        [DIPAutor(**autor.model_dump()) for autor in drucksache.autoren_anzeige]
        if drucksache.autoren_anzeige
        else []
    )

    dip_fundstelle = DIPFundstelle(**drucksache.fundstelle.model_dump(exclude={'fk_id'}))

    dip_urheber = (
        [DIPUrheber(**urheber.model_dump()) for urheber in drucksache.urheber]
        if drucksache.urheber
        else []
    )

    dip_vorgangsbezug = (
        [
            DIPVorgangsbezug(**vorgangsbezug.model_dump())
            for vorgangsbezug in drucksache.vorgangsbezug
        ]
        if drucksache.vorgangsbezug
        else []
    )

    dip_ressort = (
        [DIPRessort(**ressort.model_dump()) for ressort in drucksache.ressort]
        if drucksache.ressort
        else []
    )

    if len(dip_urheber) > 0 or len(dip_ressort) > 0:
        print("Debug")

    drucksache = DIPDrucksache(
        **drucksache.model_dump(
            exclude={
                'autoren_anzeige',
                'urheber',
                'fundstelle',
                'vorgangsbezug',
                'ressort',
            }
        ),
        autoren=dip_autoren,
        fundstelle=dip_fundstelle,
        urheber=dip_urheber,
        vorgangsbezug=dip_vorgangsbezug,
        ressort=dip_ressort,
    )

    CRUD_DIP_DRUCKSACHE.create_or_update(drucksache)


def import_vorgang(vorgang: Vorgang):
    dip_inkrafttreten = (
        [DIPInkrafttreten(**inkrafttreten.model_dump()) for inkrafttreten in vorgang.inkrafttreten]
        if vorgang.inkrafttreten
        else []
    )

    dip_verkuendung = (
        [DIPVerkuendung(**verkuendung.model_dump()) for verkuendung in vorgang.verkuendung]
        if vorgang.verkuendung
        else []
    )

    dip_vorgang_deskriptor = (
        [
            DIPVorgangDeskriptor(**vorgang_deskriptor.model_dump())
            for vorgang_deskriptor in vorgang.deskriptor
        ]
        if vorgang.deskriptor
        else []
    )

    dip_vorgang_verlinkung = (
        [
            DIPVorgangVerlinkung(**vorgang_verlinkung.model_dump())
            for vorgang_verlinkung in vorgang.vorgang_verlinkung
        ]
        if vorgang.vorgang_verlinkung
        else []
    )

    vorgang = DIPVorgang(
        **vorgang.model_dump(
            exclude={
                'inkrafttreten',
                'verkuendung',
                'deskriptor',
                'vorgang_verlinkung',
            }
        ),
        inkrafttreten=dip_inkrafttreten,
        verkuendung=dip_verkuendung,
        deskriptor=dip_vorgang_deskriptor,
        vorgang_verlinkung=dip_vorgang_verlinkung,
    )

    CRUD_DIP_VORGANG.create_or_update(vorgang)


def import_dip_bundestag():
    auth = Auth(auth_type=AuthType.DIPBUNDESTAG_API_TOKEN, token=settings.DIP_BUNDESTAG_API_KEY)
    facade = DIPBundestagFacade(settings.DIP_BUNDESTAG_BASE_URL, auth)

    drucksachen: list[Drucksache] = facade.get_drucksachen('2023-01-01T00:00:00', request_limit=1)

    for drucksache in drucksachen:
        import_drucksache(drucksache)


if __name__ == '__main__':
    import_dip_bundestag()
