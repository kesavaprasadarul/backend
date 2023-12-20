"""Bundestag Abstimmungen facade."""
import http
import logging
import typing as t
from typing import TypeVar

import requests
from pydantic import BaseModel

from backend.app.core.config import Settings
from backend.app.facades.bundestag_abstimmungen.model import (
    BundestagAbstimmungLink,
    BundestagAbstimmungLinks,
    BundestagAbstimmung,
    BundestagEinzelpersonAbstimmung,
    Vote,
)
from backend.app.facades.bundestag_abstimmungen.parameter_model import (
    BundestagAbstimmungenParameter,
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
from bs4 import BeautifulSoup, Tag
from datetime import datetime
import re
from urllib.parse import urlparse
import pandas as pd
import io
import time

_logger = logging.getLogger(__name__)

PAGE_SIZE = 30
"""Number of elements returned in a single paged response."""
DELAY_BETWEEN_REQUESTS = 0.5
RequestParams = TypeVar("RequestParams", bound=BaseModel)

MONTH_TO_NUMBER = {
    "Januar": 1,
    "Februar": 2,
    "März": 3,
    "April": 4,
    "Mai": 5,
    "Juni": 6,
    "Juli": 7,
    "August": 8,
    "September": 9,
    "Oktober": 10,
    "November": 11,
    "Dezember": 12,
}


XLSX_COL_NAME_MAPPING = {
    'Wahlperiode': 'wahlperiode',
    'Sitzungnr': 'sitzung',
    'Abstimmnr': 'abstimmung_number',
    'Fraktion/Gruppe': 'fraktion',
    'Name': 'name',
    'Vorname': 'vorname',
    'ja': 'ja',
    'nein': 'nein',
    'Enthaltung': 'enthalten',
    'ungültig': 'ungueltig',
    'nichtabgegeben': 'nicht_abgegeben',
}


class ParserError(Exception):
    """Exception raised when parsing fails."""

    pass


class BundestagAbstimmungenFacade(HttpFacade):
    data_hits: int = 0

    @classmethod
    def get_instance(cls, configuration: Settings) -> t.Self:
        _logger.info(
            'Connecting to Bundestag-Abstimmungen: %s', configuration.BUNDESTAG_ABSTIMMUNGEN_URL
        )

        auth = Auth(auth_type=AuthType.NONE)
        return cls(base_url=configuration.BUNDESTAG_ABSTIMMUNGEN_URL, auth=auth)

    def _parse_content(self, soup: BeautifulSoup) -> list[dict]:
        """Parse content from response."""

        def _parse_date(str_date: str) -> datetime:
            """Parse date from string."""
            for k, v in MONTH_TO_NUMBER.items():
                new_date = str_date.replace(k, str(v))
                if new_date != str_date:
                    return datetime.strptime(new_date, "%d. %m %Y")
            raise ParserError(f"Could not parse date: {str_date}")

        table = soup.find('table')

        if table is None:
            raise ParserError("Could not find table")
        table_body = table.find('tbody')

        if table_body is None:
            raise ParserError("Could not find table body")

        if not isinstance(table_body, Tag):
            raise ParserError("Could not find table body")

        rows = table_body.find_all('tr')

        parsed_data: list[dict] = []
        for i, row in enumerate(rows):
            cols = row.find_all('td')
            if len(cols) != 4:
                raise ParserError(f"Expected 4 columns (Row: {i}), but got {len(cols)}")

            publication_date = None
            try:
                publication_date = _parse_date(cols[0].text.strip())
            except ParserError as e:
                _logger.warn("Could not parse publication date: %s", e)

            title_raw_text = cols[2].text.strip()

            links = cols[2].find_all('a')
            if len(links) > 2:
                raise ParserError(
                    f"Expected at most 2 links (Row: {i}), but got {len(links)}: {links}"
                )
            if len(links) == 0:
                raise ParserError(f"Expected at least 1 link (Row: {i}), but got none")

            parsed_links = []

            for link in links:
                link_text = link.text.strip()
                if not 'href' in link.attrs:
                    _logger.warn("Link has no href: %s", link)
                    continue

                if link_text.lower().startswith('pdf'):
                    parsed_links.append(
                        {
                            'type': MediaType.PDF,
                            'url': link.attrs['href'],
                        }
                    )
                elif link_text.lower().startswith('xlsx'):
                    parsed_links.append(
                        {
                            'type': MediaType.XLSX,
                            'url': link.attrs['href'],
                        }
                    )
                elif link_text.lower().startswith('xls'):
                    parsed_links.append(
                        {
                            'type': MediaType.XLS,
                            'url': link.attrs['href'],
                        }
                    )
                else:
                    _logger.warn("Unknown link type: %s", link_text)

            abstimmung_date = None
            title = None
            if ':' in title_raw_text:
                if title_raw_text.startswith('08:'):
                    title_raw_text = title_raw_text.replace('08:', '08.')  # fix typo

                if title_raw_text.startswith('27.06.20130:'):
                    title_raw_text = title_raw_text.replace('27.06.20130:', '27.06.2013:')

                abstimmung_date_str, title_raw = title_raw_text.split('\n')[0].split(':', 1)
                title = title_raw.strip()

                if abstimmung_date_str.endswith('206'):
                    abstimmung_date_str = abstimmung_date_str.replace('206', '2016')  # fix typo
                try:
                    abstimmung_date = datetime.strptime(abstimmung_date_str.strip(), "%d.%m.%Y")
                except ValueError as e:
                    _logger.warn("Could not parse abstimmung date: %s", e)

            if title is None:
                title = title_raw_text.split('\n')[0].strip()
            if abstimmung_date is None:
                for link in parsed_links:
                    url_filename = link['url'].split('/')[-1]
                    if match := re.match(r'\d{8}', url_filename):
                        abstimmung_date = datetime.strptime(match.group(0), "%Y%m%d")
                        break

            if abstimmung_date is None:
                if (
                    title == 'Ergebnis der namentlichen Abstimmung zur Gesundheitsreform'
                ):  # manually set date
                    abstimmung_date = datetime(2007, 2, 2)
                else:
                    raise ParserError(f"Could not parse abstimmung date: {title_raw_text}")

            assert abstimmung_date is not None
            assert title is not None

            parsed_data.append(
                {
                    'publication_date': publication_date,
                    'title': title,
                    'abstimmung_date': abstimmung_date,
                    'links': parsed_links,
                }
            )

        return parsed_data

    def _do_paginated_request(
        self,
        method: http.HTTPMethod,
        url: str,
        *,
        params: dict | None = None,
        proxy_list: ProxyList | None = None,
        response_limit: t.Optional[int] = None,
        **kwargs,
    ) -> t.Iterator[dict]:
        """Helper to execute paginated request for REST API."""

        self.cursor = kwargs["offset"] if "offset" in kwargs else 0

        def unpack_page(paged_response: requests.Response) -> Page:
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

            new_cursor = int(meta.attrs.get('data-nextoffset', self.cursor + data_limit))

            has_next_page = new_cursor < self.data_hits

            content = self._parse_content(soup)

            if has_next_page:
                self.cursor = new_cursor
                _logger.debug('cursor: %s', self.cursor)

                # return new cursor, and add new content
                return Page(new_cursor, content)
            # there is no new page, return none as now new cursor and [] as content is already in from last iteration
            return Page(None, content)

        def get_next_page_cursor(cursor: bool) -> PageCursor | None:
            if cursor:
                return PageCursor('offset', cursor)
            return None

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

    def get_bundestag_abstimmungen_links(
        self, params: BundestagAbstimmungenParameter | None = None, response_limit: int = 1000
    ) -> t.Iterator[BundestagAbstimmungLinks]:
        param_dict = (
            params.model_dump(mode='json', exclude_none=True, by_alias=True) if params else None
        )

        for abstimmungen_links in self._do_paginated_request(
            method=http.HTTPMethod.GET,
            url="/ajax/filterlist/de/parlament/plenum/abstimmung/liste/462112-462112",
            params=param_dict,
            response_limit=response_limit,
        ):
            yield BundestagAbstimmungLinks.model_validate(abstimmungen_links)

    def get_bundestag_abstimmungen(
        self, params: BundestagAbstimmungenParameter | None = None, response_limit: int = 1000
    ) -> t.Iterator[BundestagAbstimmung]:
        def _parse_excel_abstimmung_ergebnis(
            df: pd.DataFrame,
            link_source: BundestagAbstimmungLink,
            abstimmungen_links: BundestagAbstimmungLinks,
            delay_between_requests: float = DELAY_BETWEEN_REQUESTS,
        ) -> BundestagAbstimmung:
            df = df.rename(columns=XLSX_COL_NAME_MAPPING, errors='raise')

            individual_votes = []

            for i, row in df.iterrows():
                vote = None
                if row['ja'] == 1:
                    vote = Vote.JA
                elif row['nein'] == 1:
                    vote = Vote.NEIN
                elif row['enthalten'] == 1:
                    vote = Vote.ENTHALTEN
                elif row['ungueltig'] == 1:
                    vote = Vote.UNGUELTIG
                elif row['nicht_abgegeben'] == 1:
                    vote = Vote.NICHTABGEGEBEN

                if vote is None:
                    raise ParserError(f"Could not parse vote: {row}")

                individual_votes.append(
                    BundestagEinzelpersonAbstimmung(
                        name=row['name'],
                        surname=row['vorname'],
                        fraktion=row['fraktion'],
                        vote=vote,
                    ),
                )

            total_ja = df['ja'].sum()
            total_nein = df['nein'].sum()
            total_enthalten = df['enthalten'].sum()
            total_ungueltig = df['ungueltig'].sum()
            total_nicht_abgegeben = df['nicht_abgegeben'].sum()
            sitzung = df['sitzung'].iloc[0]
            abstimmung_number = df['abstimmung_number'].iloc[0]
            wahlperiode = df['wahlperiode'].iloc[0]
            title = abstimmungen_links.title
            abstimmung_date = abstimmungen_links.abstimmung_date

            return BundestagAbstimmung(
                title=title,
                abstimmung_date=abstimmung_date,
                wahlperiode=wahlperiode,
                sitzung=sitzung,
                abstimmung_number=abstimmung_number,
                ja=total_ja,
                nein=total_nein,
                enthalten=total_enthalten,
                ungueltig=total_ungueltig,
                nicht_abgegeben=total_nicht_abgegeben,
                links=abstimmungen_links.links,
                votes=individual_votes,
                link_used=link_source,
            )

        def get_dataframe_from_excel(content: bytes, media_type: MediaType) -> pd.DataFrame:
            if media_type == MediaType.XLSX:
                df = pd.read_excel(io.BytesIO(content), engine='openpyxl')
            elif media_type == MediaType.XLS:
                df = pd.read_excel(io.BytesIO(content), engine='xlrd')
            else:
                raise ParserError(f"Unknown media type: {media_type}")
            return df

        for abstimmungen_links in self.get_bundestag_abstimmungen_links(params, response_limit):
            parsed = False
            for link in abstimmungen_links.links:
                time.sleep(delay_between_requests)
                response = self.do_request(
                    method=http.HTTPMethod.GET,
                    url_path=link.url,
                    accept_type=link.type,
                )

                response.raise_for_status()
                if link.type == MediaType.XLSX or link.type == MediaType.XLS:
                    try:
                        df = get_dataframe_from_excel(response.content, link.type)

                        yield _parse_excel_abstimmung_ergebnis(df, link, abstimmungen_links)
                        parsed = True
                        break
                    except ParserError as e:
                        _logger.warn(
                            f"Could not parse {link.type.value} for abstimmung {abstimmungen_links.title}: {e}"
                        )
                    except Exception as e:
                        _logger.error(
                            f"Could not parse {link.type.value} for abstimmung {abstimmungen_links.title}: {e}"
                        )
                elif link.type == MediaType.PDF:
                    pass
                else:
                    raise ParserError(f"Unknown media type: {link.type}")
            if not parsed:
                _logger.warn(f"Could not parse abstimmung {abstimmungen_links.title}")
