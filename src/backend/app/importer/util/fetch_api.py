import requests
import tqdm
from backend.app.importer.config import DIP_BUNDESTAG_API_KEY, API_BASE_URL
from backend.app.models.vorgang_model import VorgangModel


AUTH_HEADER = {'Authorization': DIP_BUNDESTAG_API_KEY}


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


def get_example_document():
    """
    Fetches a single document from the API.
    """
    response = _get_vorgang()

    return response['documents'][0]


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
            pbar.update(batch_size)
            response = _get_vorgang(cursor)

            yield response['documents']

            cursor = response['cursor']


def _document_to_vorgang_model(document) -> VorgangModel:
    return VorgangModel(
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
    )


def main():
    doc = get_example_document()

    vorgang_model = _document_to_vorgang_model(doc)

    print(vorgang_model)


if __name__ == '__main__':
    main()
