"""Bundestag Abstimmungen facade."""
import http
import logging
import re
import time
import typing as t
from datetime import date, datetime
from email.utils import parsedate
from functools import partial
from io import StringIO
from typing import Callable, Literal, TypeVar

import requests
import webvtt  # type: ignore
from bs4 import BeautifulSoup, Tag  # type: ignore
from pydantic import BaseModel

from backend.app.core.config import Settings
from backend.app.facades.bundestag.model import (
    BundestagAbstimmung,
    BundestagAbstimmungRedner,
    BundestagAbstimmungUrl,
    BundestagEinzelpersonAbstimmung,
    DIPRelatedDrucksache,
    Vote,
)
from backend.app.facades.bundestag.parameter_model import (
    BundestagAbstimmungenPointerParameter,
    BundestagAbstimmungParameter,
    BundestagRedeParameter,
)
from backend.app.facades.facade import (
    HTTP_REQUEST_DEFAULT_TIMEOUT_SECS,
    PAGINATION_CONTENT_ARGS_REST,
    Auth,
    AuthType,
    HttpFacade,
    MediaType,
    Page,
    PageCursor,
)
from backend.app.facades.util import ProxyList

_logger = logging.getLogger(__name__)

PAGE_SIZE = 30
"""Number of elements returned in a single paged response."""
DELAY_BETWEEN_REQUESTS = 0.3
RequestParams = TypeVar("RequestParams", bound=BaseModel)

MONTH_GERMAN_TO_ENGLISH = {
    "Januar": "January",
    "Februar": "February",
    "März": "March",
    "April": "April",
    "Mai": "May",
    "Juni": "June",
    "Juli": "July",
    "August": "August",
    "September": "September",
    "Oktober": "October",
    "November": "November",
    "Dezember": "December",
}


class ParserError(Exception):
    """Exception raised when parsing fails."""

    pass


class BundestagFacade(HttpFacade):
    data_hits: int = 0
    cursor: dict[str, int] = {
        'url_offset': 0,
    }

    @classmethod
    def get_instance(cls, configuration: Settings) -> t.Self:
        _logger.info(
            'Connecting to Bundestag-Abstimmungen: %s', configuration.BUNDESTAG_ABSTIMMUNGEN_URL
        )

        auth = Auth(auth_type=AuthType.NONE)
        return cls(base_url=configuration.BUNDESTAG_ABSTIMMUNGEN_URL, auth=auth)

    def unpack_page(
        self,
        paged_response: requests.Response,
        callable_parse_content: Callable[[BeautifulSoup], t.Iterable[dict]],
    ) -> Page:
        response_text = paged_response.text

        soup = BeautifulSoup(response_text, "html.parser")

        meta = soup.find(class_='meta-slider')

        if meta is None:
            raise ParserError("Could not find meta-slider")

        # check if meta is a tag for type hinting
        if not isinstance(meta, Tag):
            raise ParserError("Could not find meta-slider")

        if not meta.has_attr('data-hits'):
            raise ParserError("Could not find data-hits in meta-slider")

        self.data_hits = int(meta.attrs['data-hits'])

        if not meta.has_attr('data-limit'):
            _logger.warning("Could not find data-limit in meta-slider")

        if not meta.has_attr('data-nextoffset'):
            _logger.warning("Could not find data-nextoffset in meta-slider")

        data_limit = int(meta.attrs.get('data-limit', PAGE_SIZE))

        new_cursor = int(meta.attrs.get('data-nextoffset', self.cursor['url_offset'] + data_limit))

        has_next_page = new_cursor < self.data_hits

        content = callable_parse_content(soup)

        if has_next_page:
            self.cursor['url_offset'] = new_cursor
            _logger.debug('cursor: %s', self.cursor)

            # return new cursor, and add new content
            return Page(new_cursor, content)
        # there is no new page, return none as now new cursor and [] as content is already in from last iteration
        return Page(None, content)

    def _do_paginated_request(
        self,
        method: http.HTTPMethod,
        url: str,
        parse_url_content: Callable[[BeautifulSoup], t.Iterator[dict]],
        *,
        params: dict | None = None,
        proxy_list: ProxyList | None = None,
        response_limit: t.Optional[int] = None,
        **kwargs,
    ) -> t.Iterator[dict]:
        """Helper to execute paginated request for REST API."""

        self.cursor['url_offset'] = kwargs["offset"] if "offset" in kwargs else 0

        def get_next_page_cursor(cursor: int) -> PageCursor | None:
            if cursor:
                return PageCursor('offset', cursor)
            return None

        unpack_page = partial(
            self.unpack_page,
            callable_parse_content=parse_url_content,
        )

        yield from self.do_paginated_request(
            method,
            url,
            unpack_page=unpack_page,
            get_next_page_cursor=get_next_page_cursor,
            params=params,
            proxy_list=proxy_list,
            response_limit=response_limit,
            **kwargs,
        )

    def get_bundestag_abstimmung_pointers(
        self,
        params: BundestagAbstimmungenPointerParameter | None = None,
        response_limit: int = 1000,
    ) -> t.Iterator[BundestagAbstimmungUrl]:
        param_dict = (
            params.model_dump(mode='json', exclude_none=True, by_alias=True) if params else {}
        )

        if "date_start" in param_dict or "date_end" in param_dict:
            param_dict['startfield'] = 'date'

        def _parse_url_content(soup: BeautifulSoup) -> t.Iterator[dict]:
            """Parse content from response."""
            a_links = soup.find_all('a', attrs={'tabindex': '0', 'href': True})

            if a_links is None or not isinstance(a_links, list) or len(a_links) == 0:
                return []

            for a_link in a_links:
                href = a_link['href']

                match_abstimmung_id = re.match(
                    r'/parlament/plenum/abstimmung/abstimmung\?id=(\d+)', href
                )

                if match_abstimmung_id is None:
                    _logger.warning('Could not find abstimmung id in href: %s', href)
                    continue

                abstimmung_id = int(match_abstimmung_id.group(1))
                url = href

                yield {
                    'url': url,
                    'abstimmung_id': abstimmung_id,
                }

        for abstimmungen_link in self._do_paginated_request(
            method=http.HTTPMethod.GET,
            url="/ajax/filterlist/de/parlament/plenum/abstimmung/484422-484422",
            params=param_dict,
            response_limit=response_limit,
            parse_url_content=_parse_url_content,
        ):
            yield BundestagAbstimmungUrl.model_validate(abstimmungen_link)

    def get_bundestag_abstimmung(
        self,
        params: BundestagAbstimmungParameter,
        response_limit: int = 1000,
    ) -> BundestagAbstimmung:
        param_dict = params.model_dump(mode='json', exclude_none=True, by_alias=True)

        def _parse_german_date(date_german: str) -> date:
            date_english = None
            for german_month, english_month in MONTH_GERMAN_TO_ENGLISH.items():
                date_english = date_german.replace(german_month, english_month)
                if date_english != date_german:
                    break

            if date_english is None:
                raise ParserError(f"Could not parse date: {date_german}")

            try:
                return datetime.strptime(date_english, '%d. %B %Y').date()
            except ValueError as e:
                raise ParserError(
                    f"Could not parse date: {date_german} (converted to {date_english})"
                ) from e

        def _parse_vote(container: Tag, vote_container_class: str) -> int:
            regex = re.compile(r'(\d+)')
            vote_container = container.find('li', class_=vote_container_class)

            if vote_container is None:
                raise ParserError(f"Could not find {vote_container_class} container")

            vote_text = vote_container.text.strip()

            match = regex.search(vote_text)
            if match is None:
                raise ParserError(f"Could not find {vote_container_class} count")
            vote_number_text = match.group(1)

            try:
                return int(vote_number_text)
            except ValueError as e:
                raise ParserError(
                    f"Could not parse {vote_container_class} count: {vote_number_text}"
                ) from e

        def _parse_url_content(soup: BeautifulSoup) -> BundestagAbstimmung:
            bt_article = soup.find('article', class_='bt-artikel')
            if bt_article is None or not isinstance(bt_article, Tag):
                raise ParserError(
                    "Could not find bt-article (used for title, abstract and drucksachen)"
                )

            # parse date, title and abstract

            date_span = bt_article.find('span', class_='bt-date')
            if date_span is None or not isinstance(date_span, Tag):
                raise ParserError("Could not find date span")

            date_german = date_span.text.strip()

            date = _parse_german_date(date_german)

            title_header = bt_article.find('h3', class_='bt-artikel__title')
            if title_header is None:
                raise ParserError("Could not find title header")

            abstimmung_title = title_header.text.strip()

            abstract = bt_article.find('p')
            if abstract is None or not isinstance(abstract, Tag):
                raise ParserError("Could not find abstract")

            abstract = abstract.text.strip()

            # parse drucksachen
            drucksachen_links = bt_article.find_all('a', class_='dipLink', href=True)
            drucksachen = []
            for drucksache in drucksachen_links:
                drucksache_name = drucksache.text.strip()
                drucksache_url = drucksache['href']

                drucksachen.append(
                    DIPRelatedDrucksache(
                        url=drucksache_url,
                        drucksache_name=drucksache_name,
                    )
                )

            # parse voting results
            voting_results = soup.find('ul', class_='bt-chart-legend')
            if voting_results is None or not isinstance(voting_results, Tag):
                raise ParserError("Could not find voting results")

            ja_votes = _parse_vote(voting_results, 'bt-legend-ja')
            nein_votes = _parse_vote(voting_results, 'bt-legend-nein')
            enthalten_votes = _parse_vote(voting_results, 'bt-legend-enthalten')
            nicht_abgegeben_votes = _parse_vote(voting_results, 'bt-legend-na')

            # parse debatten part
            bt_redner = []
            dachzeile = None
            if (
                soup.find('a', {'href': "#debatte", 'role': 'tab', 'aria-controls': 'debatte'})
                is not None
            ):
                dachzeile_container = soup.find('span', class_='bt-dachzeile')
                if dachzeile_container is None:
                    raise ParserError("Could not find dachzeile in debatten part")

                dachzeile = dachzeile_container.text.strip()

                redner_video_links = soup.findAll('a', class_='bt-fl-teaser', href=True)
                for redner_video_link in redner_video_links:
                    if 'data-videoid' not in redner_video_link.attrs:
                        raise ParserError("Could not find data-videoid in redner video link")
                    video_id = redner_video_link.attrs['data-videoid']
                    video_url = redner_video_link.attrs['href']
                    redner_name = redner_video_link.find("h3", class_='bt-fl-teaser__text--name')
                    if redner_name is None:
                        raise ParserError("Could not find redner name")
                    redner_full_name_with_title = redner_name.text.strip()

                    redner_title, first_name, last_name = self._split_name_with_title(
                        redner_full_name_with_title, params.abstimmung_id
                    )

                    redner_function = redner_video_link.find(
                        "p", class_='bt-fl-teaser__text--function'
                    )
                    if redner_function is None:
                        raise ParserError("Could not find redner function")
                    redner_function = redner_function.text.strip()

                    redner_img = redner_video_link.find(
                        "img", {'class': 'img-responsive', 'data-img-md-normal': True}
                    )
                    if redner_img is None:
                        raise ParserError("Could not find redner image")
                    redner_image_link = redner_img.attrs['data-img-md-normal']
                    bt_redner.append(
                        BundestagAbstimmungRedner(
                            name=first_name,
                            surname=last_name,
                            title=redner_title,
                            function=redner_function,
                            video_id=video_id,
                            video_url=self.base_url + video_url,
                            image_url=self.base_url + redner_image_link,
                        )
                    )
            else:
                _logger.info("Could not find debatten part for abstimmung %s", params.abstimmung_id)
            return BundestagAbstimmung(
                id=params.abstimmung_id,
                dachzeile=dachzeile,
                title=abstimmung_title,
                abstimmung_date=date,
                ja=ja_votes,
                nein=nein_votes,
                enthalten=enthalten_votes,
                nicht_abgegeben=nicht_abgegeben_votes,
                individual_votes=[],
                drucksachen=drucksachen,
                redner=bt_redner,
            )

        resp = self.do_request(
            method=http.HTTPMethod.GET,
            url_path="parlament/plenum/abstimmung/abstimmung",
            params=param_dict,
            content_type=MediaType.HTML,
        )

        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        return _parse_url_content(soup=soup)

    @staticmethod
    def _split_name_with_title(
        full_name_with_title: str, abstimmung_id: int
    ) -> tuple[t.Optional[str], str, str]:
        """Split name with title into title, first name and last name."""
        try:
            last_name, title_surname = full_name_with_title.split(',', 1)
        except ValueError as e:
            raise ParserError(
                f"Could not split name with title (abstimmung_id: {abstimmung_id})"
            ) from e
        last_name = last_name.strip()
        title_surname = title_surname.strip()

        # handle some exceptions such as frhr.
        if 'Frhr.' in title_surname:
            title_surname = title_surname.replace('Frhr.', 'Freiherr')

        title_surname_list = title_surname.split('. ')
        if len(title_surname_list) == 1:
            title = None
            first_name = title_surname_list[0].strip()
        else:
            title = '. '.join(title_surname_list[:-1]).strip() + '.'
            first_name = title_surname_list[-1].strip()

        return title, first_name, last_name

    def get_bundestag_abstimmung_individual_votes(
        self,
        params: BundestagAbstimmungParameter,
        response_limit: int = 1000,
    ) -> t.Iterator[BundestagEinzelpersonAbstimmung]:
        param_dict = params.model_dump(mode='json', exclude_none=True, by_alias=True)

        def _parse_url_content(soup: BeautifulSoup) -> t.Iterator[BundestagEinzelpersonAbstimmung]:
            """Parse content from response."""
            abstimmung_id = params.abstimmung_id

            individual_voters = soup.findAll("div", class_='bt-slide')
            if (
                individual_voters is None
                or not isinstance(individual_voters, list)
                or len(individual_voters) == 0
            ):
                raise ParserError(
                    f"Could not find individual voters (abstimmung_id: {abstimmung_id})"
                )

            for voter in individual_voters:
                a_biography = voter.find('a', href=True)
                if a_biography is None:
                    raise ParserError(
                        f"Could not find biography link (abstimmung_id: {abstimmung_id})"
                    )
                biography_link = a_biography['href']

                img = voter.find('img', {"data-img-md-normal": True})
                img_url = None
                if img is not None and img['data-img-md-normal']:
                    img_url = img['data-img-md-normal']
                    if img_url.startswith('/'):
                        img_url = self.base_url + img_url

                voter_information = voter.find('div', class_='bt-teaser-person-text')
                if voter_information is None:
                    raise ParserError(
                        f"Could not find voter information (abstimmung_id: {abstimmung_id})"
                    )

                # parse name of the person + title
                name_header = voter_information.find('h3')
                if name_header is None:
                    raise ParserError(
                        f"Could not find name header (abstimmung_id: {abstimmung_id})"
                    )
                full_name_with_title = name_header.text.strip()

                if full_name_with_title is None:
                    raise ParserError(
                        f"Could not find full name with title (abstimmung_id: {abstimmung_id})"
                    )

                title, first_name, last_name = self._split_name_with_title(
                    full_name_with_title, abstimmung_id
                )

                # parse party of the person
                fraction_container = voter_information.find('p', class_='bt-person-fraktion')
                if fraction_container is None:
                    raise ParserError(
                        f"Could not find fraction of {first_name + ' ' + last_name} (abstimmung_id: {abstimmung_id})"
                    )
                fraction = fraction_container.text.strip()

                # parse vote of the person
                if voter_information.find('p', class_='bt-abstimmung-ja'):
                    vote = Vote.JA
                elif voter_information.find('p', class_='bt-abstimmung-nein'):
                    vote = Vote.NEIN
                elif voter_information.find('p', class_='bt-abstimmung-enthalten'):
                    vote = Vote.ENTHALTEN
                elif voter_information.find('p', class_='bt-abstimmung-na'):
                    vote = Vote.NICHTABGEGEBEN
                else:
                    raise ParserError(
                        f"Could not find vote of {first_name + ' ' + last_name} (abstimmung_id: {abstimmung_id})"
                    )

                bundesland = None
                if 'data-bundesland' in voter_information.attrs:
                    bundesland = voter_information.attrs['data-bundesland']
                else:
                    logging.warning(
                        f"Could not find bundesland of {first_name + ' ' + last_name} (abstimmung_id: {abstimmung_id})"
                    )

                yield BundestagEinzelpersonAbstimmung(
                    name=first_name,
                    surname=last_name,
                    title=title,
                    fraktion=fraction,
                    vote=vote,
                    image_url=img_url,
                    biography_url=self.base_url + biography_link,
                    bundesland=bundesland,
                )

        resp = self.do_request(
            method=http.HTTPMethod.GET,
            url_path="/apps/na/na/namensliste.form",
            params=param_dict,
            content_type=MediaType.HTML,
        )

        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        yield from _parse_url_content(soup=soup)

    def get_bundestag_rede_text(self, params: BundestagRedeParameter) -> str:
        param_dict = params.model_dump(mode='json', exclude_none=True, by_alias=True)

        param_dict['application'] = 144277506

        resp = self.do_request(
            method=http.HTTPMethod.GET,
            url_path="/pservices/player/vtt",
            params=param_dict,
            content_type=MediaType.HTML,
            base_url="https://webtv.bundestag.de/",
        )

        resp.raise_for_status()

        payload = resp.content.decode("utf-8")
        buffer = StringIO(payload)

        clean_text = ""
        for caption in webvtt.read_buffer(buffer):
            clean_text += caption.text.replace('\n', ' ').strip() + " "

        return clean_text
