from typing import Callable, Iterator, TypeVar

from backend.app.core.config import settings
from backend.app.crud.base import CRUDBase
from backend.app.crud.CRUDDIPBundestag.crud_drucksache import CRUD_DIP_DRUCKSACHE
from backend.app.crud.CRUDDIPBundestag.crud_vorgang import CRUD_DIP_VORGANG
from backend.app.crud.CRUDDIPBundestag.crud_vorgangsposition import CRUD_DIP_VORGANGSPOSITION
from backend.app.db.database import Base
from backend.app.facades.deutscher_bundestag.facade import DIPBundestagFacade
from backend.app.facades.deutscher_bundestag.model import Drucksache, Vorgang, Vorgangsposition
from backend.app.facades.util import ProxyList
from backend.app.models.deutscher_bundestag.drucksache_model import (
    DIPAutor,
    DIPDrucksache,
    DIPVorgangsbezug,
)
from backend.app.models.deutscher_bundestag.fundstelle_model import DIPFundstelle
from backend.app.models.deutscher_bundestag.ressort_model import DIPRessort
from backend.app.models.deutscher_bundestag.plenarprotokoll_model import (
    DIPPlenarprotokoll,
)  # flake8: noqa
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

ModelType = TypeVar("ModelType", bound=Base)
PydanticModelType = TypeVar("PydanticModelType")


def drucksache_transform_to_db_model(drucksache: Drucksache) -> DIPDrucksache:
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
            DIPVorgangsbezug(
                **vorgangsbezug.model_dump(exclude={'id'}), vorgang_id=vorgangsbezug.id
            )
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

    return DIPDrucksache(
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


def vorgang_transform_to_db_model(vorgang: Vorgang) -> DIPVorgang:
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

    return DIPVorgang(
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


def vorgangsposition_transform_to_db_model(
    vorgangsposition: Vorgangsposition,
) -> DIPVorgangsposition:
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

    return DIPVorgangsposition(
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


def batch_upsert(
    transform: Callable[[PydanticModelType], ModelType],
    crud: CRUDBase[ModelType],
    pydantic_models: Iterator[PydanticModelType],
    upsert_batch_size: int = 100,
):
    batch = []
    batch_count = 1
    for pydantic_model in pydantic_models:
        model = transform(pydantic_model)
        batch.append(model)

        if len(batch) >= upsert_batch_size:
            print(f'Upserting batch {batch_count} into {model.__tablename__}-Table.')
            crud.create_or_update_multi(batch)
            batch = []
            batch_count += 1

    if batch:
        print(f'Upserting final batch ({batch_count}) into {batch[0].__tablename__}-Table.')
        crud.create_or_update_multi(batch)


def import_drucksachen(
    facade: DIPBundestagFacade,
    since_datetime: str,
    response_limit: int | None = None,
    proxy_list: ProxyList | None = None,
    upsert_batch_size: int = 100,
):
    drucksachen = facade.get_drucksachen(
        since_datetime=since_datetime, response_limit=response_limit, proxy_list=proxy_list
    )

    crud = CRUD_DIP_DRUCKSACHE

    batch_upsert(
        transform=drucksache_transform_to_db_model,
        crud=crud,
        pydantic_models=drucksachen,
        upsert_batch_size=upsert_batch_size,
    )


def import_vorgangspositionen(
    facade: DIPBundestagFacade,
    since_datetime: str,
    response_limit: int | None = None,
    proxy_list: ProxyList | None = None,
    upsert_batch_size: int = 100,
):
    vorgangspositionen = facade.get_vorgangspositionen(
        since_datetime=since_datetime, response_limit=response_limit, proxy_list=proxy_list
    )

    crud = CRUD_DIP_VORGANGSPOSITION

    batch_upsert(
        transform=vorgangsposition_transform_to_db_model,
        crud=crud,
        pydantic_models=vorgangspositionen,
        upsert_batch_size=upsert_batch_size,
    )


def import_vorgang(
    facade: DIPBundestagFacade,
    since_datetime: str,
    response_limit: int | None = None,
    proxy_list: ProxyList | None = None,
    upsert_batch_size: int = 100,
):
    vorgange = facade.get_vorgange(
        since_datetime=since_datetime, response_limit=response_limit, proxy_list=proxy_list
    )

    crud = CRUD_DIP_VORGANG

    batch_upsert(
        transform=vorgang_transform_to_db_model,
        crud=crud,
        pydantic_models=vorgange,
        upsert_batch_size=upsert_batch_size,
    )


def import_dip_bundestag():
    facade = DIPBundestagFacade.get_instance(settings)

    proxy_list = ProxyList.from_url(settings.PROXY_LIST_URL)

    import_vorgangspositionen(
        facade=facade, since_datetime='2016-01-01T00:00:00', proxy_list=proxy_list, response_limit=1
    )


if __name__ == '__main__':
    import_dip_bundestag()
