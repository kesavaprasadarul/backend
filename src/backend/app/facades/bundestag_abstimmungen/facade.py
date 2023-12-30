"""Bundestag Abstimmungen facade."""
from email.utils import parsedate
import http
import logging
import typing as t
from typing import TypeVar

import requests
from pydantic import BaseModel

from backend.app.core.config import Settings
from backend.app.facades.bundestag_abstimmungen.model import (
    BundestagAbstimmungUrl,
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
import time
from typing import Callable, Literal
from functools import partial

_logger = logging.getLogger(__name__)

PAGE_SIZE = 30
"""Number of elements returned in a single paged response."""
DELAY_BETWEEN_REQUESTS = 0.3
RequestParams = TypeVar("RequestParams", bound=BaseModel)


class ParserError(Exception):
    """Exception raised when parsing fails."""

    pass


class BundestagAbstimmungenFacade(HttpFacade):
    data_hits: int = 0
    cursor: dict[str, int] = {
        'url_offset': 0,
        'party_offset': 0,
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
        params: BundestagAbstimmungenParameter | None = None,
        response_limit: int = 1000,
    ) -> t.Iterator[BundestagAbstimmungUrl]:
        param_dict = (
            params.model_dump(mode='json', exclude_none=True, by_alias=True) if params else None
        )

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

    def get_bundestag_abstimmungen_individual_votes(
        self,
        abstimmung_id: int,
        params: BundestagAbstimmungenParameter | None = None,
        response_limit: int = 1000,
    ) -> t.Iterator[BundestagEinzelpersonAbstimmung]:
        endpoint = "apps/na/na/namensliste.form"
        pass
