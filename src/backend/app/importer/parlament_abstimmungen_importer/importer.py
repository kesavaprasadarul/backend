from backend.app.facades.bundestag_abstimmungen.parameter_model import (
    BundestagAbstimmungenParameter,
)
from backend.app.facades.bundestag_abstimmungen.model import (
    BundestagAbstimmungUrl,
    BundestagAbstimmung,
    BundestagEinzelpersonAbstimmung,
    Vote,
)
from backend.app.utils import get_data_folder
from backend.app.facades.bundestag_abstimmungen.facade import BundestagAbstimmungenFacade
from backend.app.core.config import settings
from backend.app.core.logging import configure_logging
from datetime import date


class BundestagAbstimmungenImporter:
    def __init__(self):
        self.facade = BundestagAbstimmungenFacade.get_instance(settings)
        self.data_folder = get_data_folder()

    def get_abstimmungen(
        self, params: BundestagAbstimmungenParameter | None = None, response_limit: int = 1000
    ):
        for abstimmung_pointer in self.facade.get_bundestag_abstimmung_pointers(
            params=params, response_limit=response_limit
        ):
            individual_abstimmunge: list[
                BundestagEinzelpersonAbstimmung
            ] = self.facade.get_bundestag_abstimmungen_individual_votes(
                abstimmung_pointer.abstimmung_id
            )


def main():
    importer = BundestagAbstimmungenImporter()

    params = BundestagAbstimmungenPointerParameter(
        date_start=date(2021, 1, 1), date_end=date(2023, 12, 31)
    )

    for abstimmung in importer.get_abstimmungen(params=params):
        print(abstimmung)


if __name__ == '__main__':
    configure_logging()
    main()
