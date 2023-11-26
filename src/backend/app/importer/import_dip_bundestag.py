from backend.app.core.config import settings
from backend.app.crud.CRUDDIPBundestag.crud_drucksache import CRUD_DIP_DRUCKSACHE
from backend.app.crud.CRUDDIPBundestag.crud_vorgang import CRUD_DIP_VORGANG
from backend.app.crud.CRUDDIPBundestag.crud_vorgangsposition import CRUD_DIP_VORGANGSPOSITION
from backend.app.facades.deutscher_bundestag.facade import DIPBundestagFacade
from backend.app.facades.deutscher_bundestag.model import Drucksache, Vorgang, Vorgangsposition
from backend.app.facades.facade import Auth, AuthType
from backend.app.models.deutscher_bundestag.drucksache_model import (
    DIPAutor,
    DIPDrucksache,
    DIPVorgangsbezug,
)
from backend.app.models.deutscher_bundestag.fundstelle_model import DIPFundstelle
from backend.app.models.deutscher_bundestag.ressort_model import DIPRessort
from backend.app.models.deutscher_bundestag.urheber_model import DIPUrheber
from backend.app.models.deutscher_bundestag.vorgang_model import (
    DIPInkrafttreten,
    DIPVerkuendung,
    DIPVorgang,
    DIPVorgangDeskriptor,
    DIPVorgangVerlinkung,
)
from backend.app.models.deutscher_bundestag.vorgangsposition_model import (
    DIPAktivitaetAnzeige,
    DIPBeschlussfassung,
    DIPUeberweisung,
    DIPVorgangsposition,
    DIPVorgangspositionbezug,
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


def import_vorgangsposition(vorgangsposition: Vorgangsposition):
    dip_aktivitaet_anzeige = (
        [
            DIPAktivitaetAnzeige(**aktivitaet_anzeige.model_dump())
            for aktivitaet_anzeige in vorgangsposition.aktivitaet_anzeige
        ]
        if vorgangsposition.aktivitaet_anzeige
        else []
    )

    dip_vorgangspositionbezug = (
        [
            DIPVorgangspositionbezug(
                **vorgangspositionbezug.model_dump(
                    exclude={'id'},
                ),
                from_vorgang_id=vorgangsposition.vorgang_id,
                to_vorgang_id=vorgangspositionbezug.id,
            )
            for vorgangspositionbezug in vorgangsposition.mitberaten
        ]
        if vorgangsposition.mitberaten
        else []
    )

    dip_ueberweisung = (
        [
            DIPUeberweisung(**ueberweisung.model_dump())
            for ueberweisung in vorgangsposition.ueberweisung
        ]
        if vorgangsposition.ueberweisung
        else []
    )

    dip_beschlussfassung = (
        [
            DIPBeschlussfassung(**beschlussfassung.model_dump())
            for beschlussfassung in vorgangsposition.beschlussfassung
        ]
        if vorgangsposition.beschlussfassung
        else []
    )

    dip_fundstelle = (
        DIPFundstelle(**vorgangsposition.fundstelle.model_dump(exclude={'fk_id'}))
        if vorgangsposition.fundstelle
        else None
    )

    dip_urheber = (
        [DIPUrheber(**urheber.model_dump()) for urheber in vorgangsposition.urheber]
        if vorgangsposition.urheber
        else []
    )

    dip_ressort = (
        [DIPRessort(**ressort.model_dump()) for ressort in vorgangsposition.ressort]
        if vorgangsposition.ressort
        else []
    )

    vorgangsposition = DIPVorgangsposition(
        **vorgangsposition.model_dump(
            exclude={
                'aktivitaet_anzeige',
                'ueberweisung',
                'beschlussfassung',
                'fundstelle',
                'urheber',
                'ressort',
                'mitberaten',
            }
        ),
        aktivitaet_anzeige=dip_aktivitaet_anzeige,
        ueberweisung=dip_ueberweisung,
        beschlussfassung=dip_beschlussfassung,
        fundstelle=dip_fundstelle,
        urheber=dip_urheber,
        ressort=dip_ressort,
        vorgangspositionbezug=dip_vorgangspositionbezug,
    )

    CRUD_DIP_VORGANGSPOSITION.create_or_update(vorgangsposition)


def import_dip_bundestag():
    auth = Auth(auth_type=AuthType.DIPBUNDESTAG_API_TOKEN, token=settings.DIP_BUNDESTAG_API_KEY)
    facade = DIPBundestagFacade(settings.DIP_BUNDESTAG_BASE_URL, auth)

    # drucksachen: list[Drucksache] = facade.get_drucksachen('2023-01-01T00:00:00', request_limit=1)

    # for drucksache in drucksachen:
    #     import_drucksache(drucksache)

    # vorgange = facade.get_vorgange('2023-01-01T00:00:00', request_limit=1)

    # for vorgang in vorgange:
    #     import_vorgang(vorgang)

    vorgangspositionen = facade.get_vorgangspositionen('2023-01-01T00:00:00', request_limit=1)

    for vorgangsposition in vorgangspositionen:
        import_vorgangsposition(vorgangsposition)


if __name__ == '__main__':
    import_dip_bundestag()
