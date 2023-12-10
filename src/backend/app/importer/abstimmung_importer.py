from datetime import date, datetime, timedelta
from enum import Enum
from logging import getLogger
from sqlite3 import Date

from pydantic import BaseModel, Field

from backend.app.core.logging import configure_logging
from backend.app.crud.CRUDApi import crud_abstimmung
from backend.app.crud.CRUDApi.crud_abstimmung import CRUD_Abstimmung
from backend.app.crud.CRUDDIPBundestag.crud_drucksache import CRUD_DIP_DRUCKSACHE, CountsPerWeek
from backend.app.facades.deutscher_bundestag.model import DrucksacheTextListResponse, Zuordnung
from backend.app.facades.deutscher_bundestag.parameter_model import DrucksacheParameter
from backend.app.importer.dip_importer.dip_drucksache_importer import DIPBundestagDrucksacheImporter

_logger = getLogger(__name__)


class FetchTypes(str, Enum):
    FULL = "full"
    NEW = "new"
    MISSING = "missing"


def _create_drucksache_parameter_list(
    drucksachetyp_list: list[str] | None = None,
    datum_start: date | None = None,
    datum_end: date | None = None,
    aktualisiert_start: datetime | None = None,
    vorgangstypen: list[str] | None = None,
) -> list[DrucksacheParameter]:
    """Generate DrucksacheParameter list."""
    drucksache_parameter_list = []

    if drucksachetyp_list is None:
        return [
            DrucksacheParameter(
                datum_start=datum_start,
                datum_end=datum_end,
                aktualisiert_start=aktualisiert_start,
                vorgangstyp=vorgangstypen,
            )
        ]
    # get all drucksache_parameter
    for drucksache_typ in drucksachetyp_list:
        drucksache_parameter_list.append(
            DrucksacheParameter(
                datum_start=datum_start,
                datum_end=datum_end,
                aktualisiert_start=aktualisiert_start,
                drucksachetyp=drucksache_typ,
                vorgangstyp=vorgangstypen,
            )
        )

    return drucksache_parameter_list


def _import_relevant_beschlussfassungen(
    drucksache_importer: DIPBundestagDrucksacheImporter,
    fetch: FetchTypes = FetchTypes.NEW,
    date_start: date | None = None,
    date_end: date | None = None,
    drucksachetyp_filter: list[str] | None = None,
    vorgangstyp_filter: list[str] | None = None,
):
    param_list: list[DrucksacheParameter] = []

    if fetch == FetchTypes.NEW:
        param_list.extend(
            _create_drucksache_parameter_list(
                drucksachetyp_list=drucksachetyp_filter,
                vorgangstypen=vorgangstyp_filter,
                aktualisiert_start=datetime.now() - timedelta(minutes=30),
            )
        )
    elif fetch == FetchTypes.FULL:
        param_list.extend(
            _create_drucksache_parameter_list(
                drucksachetyp_list=drucksachetyp_filter,
                datum_start=date_start,
                datum_end=date_end,
                vorgangstypen=vorgangstyp_filter,
            )
        )
    elif fetch == FetchTypes.MISSING:
        if date_start is None:
            raise ValueError("date_start must be set if fetch is set to 'missing'")
        if date_end is None:
            raise ValueError("date_end must be set if fetch is set to 'missing'")
        db_counts_per_week: list[CountsPerWeek] = CRUD_DIP_DRUCKSACHE.read_count_per_week(
            date_start,
            date_end,
            drucksachetyp_filter,
            vorgangstyp_filter,
        )

        _logger.info("Comparing Drucksachen counts per week with API counts per week")

        for count_per_week in db_counts_per_week:
            count_param_list = _create_drucksache_parameter_list(
                drucksachetyp_list=drucksachetyp_filter,
                datum_start=count_per_week.week_start_date,
                datum_end=count_per_week.week_end_date,
                vorgangstypen=vorgangstyp_filter,
            )

            api_drucksache_count = 0
            params_with_at_least_one_drucksache = []

            for drucksachetyp_count_param in count_param_list:
                count_drucksache = drucksache_importer.fetch_count(params=drucksachetyp_count_param)
                if count_drucksache > 0:
                    params_with_at_least_one_drucksache.append(drucksachetyp_count_param)
                api_drucksache_count += count_drucksache

            if api_drucksache_count > count_per_week.drucksache_count:
                _logger.debug(
                    "Found %s (imported: %s) unimported Drucksachen in year-week %s-%s",
                    api_drucksache_count - count_per_week.drucksache_count,
                    count_per_week.drucksache_count,
                    count_per_week.year,
                    count_per_week.week,
                )
                param_list.extend(params_with_at_least_one_drucksache)

        _logger.info(
            "Comparing Drucksachen counts per week with API counts per week finished. Found %s Drucksachen-Parameters to import.",
            len(param_list),
        )

    _logger.info("Start import of data")

    for param in param_list:
        _logger.debug("Importing Drucksachen with parameter %s", param)
        drucksache_importer.import_data(param)
        _logger.debug("Importing Drucksachen with parameter %s finished", param)

    _logger.info("Imported %s Drucksachen.", drucksache_importer.get_imported_count())


def import_abstimmungen(
    fetch: FetchTypes,
    date_start: date | None = None,
    date_end: date | None = None,
):
    # Base parameters that we need for meaninungful abstimmungen
    drucksachetyp_filter = [
        'Beschluss',
        'Gesetzgebung',
        'Beschlussempfehlung und Bericht',
        'Empfehlungen',
    ]
    vorgangstyp_filter = [
        "Antrag",
        "Entschließungsantrag BT",
        "Gesetzgebung",
        "Rechtsverordnung",
        "Untersuchungsausschuss",
        "Wahl im BT",
    ]
    drucksache_importer = DIPBundestagDrucksacheImporter(
        import_vorgaenge=True, import_vorgangspositionen=True
    )

    _import_relevant_beschlussfassungen(
        drucksache_importer,
        fetch=fetch,
        date_start=date_start,
        date_end=date_end,
        drucksachetyp_filter=drucksachetyp_filter,
        vorgangstyp_filter=vorgangstyp_filter,
    )

    imported_count = drucksache_importer.get_imported_count()

    if imported_count == 0:
        _logger.info("No new Drucksachen found. No abstimmungen imported.")
        return

    _logger.info("Imported %s Drucksachen.", imported_count)

    # CRUD_Abstimmung.update_abstimmungen(drucksachetyp_filter, vorgangstyp_filter)


if __name__ == "__main__":
    configure_logging()
    import_abstimmungen(
        fetch=FetchTypes.MISSING,
        date_start=date(2023, 12, 1),
        date_end=(date.today() + timedelta(weeks=1)),
    )
