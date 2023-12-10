"""Method for loading plenarprotokoll data, analyzing it, and storing results to sql table bundestag_top_topics."""
import calendar
import datetime
import itertools
import logging

from backend.app.app_logic.landing_page.word_analyser import WordCounter
from backend.app.core.config import Settings
from backend.app.facades.deutscher_bundestag.facade import DIPBundestagFacade
from backend.app.facades.deutscher_bundestag.model import Zuordnung
from backend.app.facades.deutscher_bundestag.model_plenarprotokoll_vorgangsbezug import (
    PlenarprotokollVorgangsbezug,
)
from backend.app.facades.deutscher_bundestag.parameter_model import PlenarprotokollParameter

_logger = logging.getLogger(__name__)


def get_bundestag_top_topics_for_month(month: int, year: int):
    """Get top topics of bundestags for given month and year.

    Args:
        month (int): Month for which to get the top topics of Bundestags Plenarprotokolle.
        year (int): Year for which to get the top topics of Bundestags Plenarprotokolle.
    """
    # data fetching
    dip_bundestag_facade = DIPBundestagFacade.get_instance(Settings())
    date_start = datetime.date(year, month, 1)
    date_end = datetime.date(year, month, calendar.monthrange(year, month)[1])
    _logger.info(
        "Fetch plenarprotokolle with date_start='%s' and date_end='%s'", date_start, date_end
    )
    plenarprotokolle = dip_bundestag_facade.get_plenarprotokolle(
        PlenarprotokollParameter(datum_start=date_start, datum_end=date_end, zuordnung=Zuordnung.BT)
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

    top_topics_by_ressort = {}
    for key in topics_by_ressort.keys():
        top_topics_by_ressort[key] = sorted(
            topics_by_ressort[key], key=lambda x: x[1], reverse=True
        )[0:5]

    return top_topics_by_ressort
