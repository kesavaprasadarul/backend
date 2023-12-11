from backend.app.crud.CRUDApi.crud_mandate import CRUD_Mandate
from logging import getLogger
import csv
import os
from backend.app.models.api.mandate_model import APIMandate
import asyncio
from datetime import datetime

_logger = getLogger(__name__)

from backend.app.utils import get_data_folder

FILE_NAME = 'mandate.csv'


def _read_mandate(mandate: list[APIMandate], file) -> list[APIMandate]:
    with open(
        file,
        "r",
        encoding="utf-8",
        newline="",
    ) as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        next(reader, None)
        for row in reader:
            mandate.append(
                APIMandate(
                    id=int(row[0]),
                    wahlperiode=int(row[1]),
                    anzahl_stimmberechtigt=int(row[2]),
                    date_from=datetime.strptime(row[3], "%Y-%m-%d").date()
                    if row[3] != ''
                    else None,
                    date_to=datetime.strptime(row[4], "%Y-%m-%d").date() if row[4] != '' else None,
                    comment=row[5] if row[5] != '' else None,
                )
            )
    return mandate


def import_mandate() -> None:
    _logger.info("Import Mandate")
    file = os.path.join(get_data_folder(), FILE_NAME)

    if not os.path.exists(file):
        _logger.error(f'Mandate-Data {file} does not exist')
        raise FileNotFoundError(f'Mandate-Data {file} does not exist.')

    mandate: list[APIMandate] = []

    CRUD_Mandate.create_or_update_multi(_read_mandate(mandate, file))

    _logger.info("Import Mandate finished")


if __name__ == '__main__':
    import_mandate()
