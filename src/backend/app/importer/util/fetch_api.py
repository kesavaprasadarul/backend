import requests
import tqdm
from backend.app.importer.config import DIP_BUNDESTAG_API_KEY, API_BASE_URL
from backend.app.importer.facades.bundestag_dip.vorgang_model import (
    VorgangModel,
    VorgangDeskriptorModel,
    VorgangDeskriptorTyp,
)
from backend.app.db.database import Base, SessionLocal
from psycopg2 import IntegrityError
from sqlalchemy.exc import OperationalError
import logging
from typing import TypeVar

AUTH_HEADER = {'Authorization': DIP_BUNDESTAG_API_KEY}

_logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=Base)  # pylint: disable=invalid-name


def multi_upsert(obj_in_list: list[ModelType]) -> list[ModelType] | None:
    db = SessionLocal()
    try:
        for obj_in in obj_in_list:
            db.merge(obj_in)
        db.commit()
    except IntegrityError as error:
        db.flush()
        db.rollback()
        raise error
    except OperationalError as error:
        # if database closed unexpectedly, OperationalError occurs
        _logger.error("%s occured. Session will be rolled back.", error)
        db.rollback()
        for obj_in in obj_in_list:
            db.merge(obj_in)
        db.commit()
    return obj_in_list


def _get_vorgang_by_id(vorgang_id: int):
    """
    Fetches a single document from the API.
    """
    url = f"{API_BASE_URL}/vorgang/{vorgang_id}"

    response = requests.get(url, headers=AUTH_HEADER)

    response.raise_for_status()

    return response.json()


def _get_vorgang(cursor: str | None = None):
    """
    Fetches all vorgange from the API.
    """
    url = f"{API_BASE_URL}/vorgang"
    if cursor:
        url += f"?cursor={cursor}"

    response = requests.get(url, headers=AUTH_HEADER)

    response.raise_for_status()

    return response.json()


def get_example_document(document_id: int | None = None):
    """
    Fetches a single document from the API.
    """
    if document_id:
        response_json = _get_vorgang_by_id(document_id)
        return response_json
    else:
        response_json = _get_vorgang()
        return response_json['documents'][0]


def get_all_vorgang():
    """
    Fetches all vorgange from the API.
    """
    init_response = _get_vorgang()

    cursor = init_response['cursor']

    batch_size = len(init_response['documents'])
    total_size = init_response['numFound']
    batches = total_size // batch_size

    yield init_response['documents']

    with tqdm.tqdm(
        total=total_size,
        initial=batch_size,
    ) as pbar:
        for _ in range(batches):
            print("Current Cursor: ", cursor)
            pbar.update(batch_size)
            response = _get_vorgang(cursor)

            yield response['documents']

            cursor = response['cursor']


def _document_to_vorgang_model(document) -> VorgangModel:
    vorgang_deskriptor_models = []
    for vorgang_deskriptor in document.get('deskriptor', []):
        vorgang_deskriptor_models.append(
            VorgangDeskriptorModel(
                name=vorgang_deskriptor['name'],
                typ=VorgangDeskriptorTyp(vorgang_deskriptor['typ']),
                fundstelle=vorgang_deskriptor['fundstelle'],
            )
        )

    vorgang_model = VorgangModel(
        id=document['id'],
        typ=document['typ'],
        beratungsstand=document.get('beratungsstand'),
        vorgangstyp=document['vorgangstyp'],
        wahlperiode=document.get('wahlperiode'),
        initiative=document.get('initiative'),
        datum=document.get('datum'),
        aktualisiert=document['aktualisiert'],
        titel=document['titel'],
        abstract=document.get('abstract'),
        sachgebiet=document.get('sachgebiet'),
        gesta=document.get('gesta'),
        zustimmungsbeduerftigkeit=document.get('zustimmungsbeduerftigkeit'),
        kom=document.get('kom'),
        ratsdok=document.get('ratsdok'),
        # verkuendung_id=document['verkuendung_id'],
        inkrafttreten_datum=document.get('inkrafttreten_datum'),
        inkrafttreten_erlaeuterung=document.get('inkrafttreten_erlaeuterung'),
        archiv=document.get('archiv'),
        # vorgang_verlinkung_id=document['vorgang_verlinkung_id'],
        sek=document.get('sek'),
        deskriptor=vorgang_deskriptor_models,
    )

    return vorgang_model


def upsert_single_document(document_id: int = 305714):
    doc = get_example_document(document_id=document_id)

    vorgang_model = _document_to_vorgang_model(doc)

    multi_upsert([vorgang_model])


def upsert_all_documents():
    for batch in get_all_vorgang():
        vorgang_models = []
        for doc in batch:
            vorgang_model = _document_to_vorgang_model(doc)
            vorgang_models.append(vorgang_model)

        multi_upsert(vorgang_models)


def main():
    # upsert_single_document()
    upsert_all_documents()


if __name__ == '__main__':
    main()
