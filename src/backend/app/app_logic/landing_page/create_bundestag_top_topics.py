"""Method for loading plenarprotokoll data, analyzing it, and storing results to sql table bundestag_top_topics."""
import calendar
import datetime
import itertools
import logging
from typing import Optional

from backend.app.app_logic.landing_page.word_analyser import WordCounter
from backend.app.core.config import Settings
from backend.app.crud.CRUDApi.crud_top_topics import CRUD_TOP_TOPICS
from backend.app.facades.deutscher_bundestag.facade import DIPBundestagFacade
from backend.app.facades.deutscher_bundestag.model import Zuordnung
from backend.app.facades.deutscher_bundestag.model_plenarprotokoll_vorgangsbezug import (
    PlenarprotokollVorgangsbezug,
)
from backend.app.facades.deutscher_bundestag.parameter_model import PlenarprotokollParameter
from backend.app.models.api.top_topics_model import TopTopics

_logger = logging.getLogger(__name__)


def create_bundestag_top_topics(
    month: Optional[int] = None, year: Optional[int] = None, election_period: Optional[int] = None
):
    """Create top topics of bundestag from plenarprotkoll for given timerange and store to database table top_topics.

    Args:
        month (int): Month for which to get the top topics of Bundestags Plenarprotokolle.
        year (int): Year for which to get the top topics of Bundestags Plenarprotokolle.
        election_period (int): Elec
    """
    if (
        month and year and not election_period
    ):  # election_period will be ignored if given (only month and year is considerd)
        date_start = datetime.date(year, month, 1)
        date_end = datetime.date(year, month, calendar.monthrange(year, month)[1])
    elif year and not month and not election_period:
        date_start = datetime.date(year, 1, 1)
        date_end = datetime.date(year, 12, calendar.monthrange(year, 12)[1])
    elif election_period and not year and not month:
        # take election_period as it is
        pass
    else:
        _logger.error(
            "Check your params, api endpoint allows only 3 different combinations: month and year, only year, only election_period."
        )

    # data fetching
    dip_bundestag_facade = DIPBundestagFacade.get_instance(Settings())
    _logger.info(
        "Fetch plenarprotokolle with date_start='%s' and date_end='%s'", date_start, date_end
    )
    plenarprotokolle = dip_bundestag_facade.get_plenarprotokolle(
        PlenarprotokollParameter(
            datum_start=date_start,
            datum_ende=date_end,
            wahlperiode=[election_period] if election_period else None,
            zuordnung=Zuordnung.BT,
        )
    )

    plenarprotokoll_vorgangsbezuege: list[PlenarprotokollVorgangsbezug] = []
    for plenarprotokoll in plenarprotokolle:
        _logger.info("Fetch vorgangsbezuge for plenarprotokoll with id %d", plenarprotokoll.id)
        plenarprotokoll_vorgangsbezuege.extend(
            dip_bundestag_facade.get_vorgangsbezuege_of_plenarprotokoll_by_id(
                plenarprotokoll_id=plenarprotokoll.id
            )
        )

    plenarprotokoll_vorgangsbezuege_abstract: list[str] = [
        vorgangsbezug.abstract or vorgangsbezug.titel
        for vorgangsbezug in plenarprotokoll_vorgangsbezuege
    ]  # either get abstract or title and add to list
    plenarprotokoll_vorgangsbezuege_abstract_split = list(
        itertools.chain.from_iterable(
            [abstract.split() for abstract in plenarprotokoll_vorgangsbezuege_abstract]
        )
    )

    # word counter for analysing
    word_analyser = WordCounter(plenarprotokoll_vorgangsbezuege_abstract_split)
    topics_by_ressort = word_analyser.make_word_cloud()

    top_topics_by_ressort: dict[str, list[list]] = {}
    for key in topics_by_ressort.keys():
        top_topics_by_ressort[key] = sorted(
            topics_by_ressort[key], key=lambda x: x[1], reverse=True
        )[0:5]

    # store to db
    for key in top_topics_by_ressort:
        CRUD_TOP_TOPICS.create_or_update_multi(
            [
                TopTopics(
                    month=month,
                    year=year,
                    election_period=election_period,
                    ressort=key,
                    word=word_and_value[0],
                    value=word_and_value[1],
                )
                for word_and_value in top_topics_by_ressort[key]
            ]
        )

    return top_topics_by_ressort
