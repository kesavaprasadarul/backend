"""DIP Bundestag facade."""
import datetime
import http
import logging
import typing as t

import requests

from backend.app.core.config import Settings
from backend.app.facades.deutscher_bundestag.model import (
    Drucksache,
    DrucksacheText,
    Plenarprotokoll,
    PlenarprotokollText,
    Vorgang,
    Vorgangsposition,
)
from backend.app.facades.deutscher_bundestag.model_plenarprotokoll_vorgangsbezug import (
    PlenarprotokollVorgangsbezug,
)
from backend.app.facades.facade import (
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


PAGE_SIZE = 100
"""Number of elements returned in a single paged response."""


class DIPBundestagFacade(HttpFacade):
    """Facade implementation for a DIP Bundestag.

    For more information look at docu of DIP bundestag API:
    https://dip.bundestag.de/%C3%BCber-dip/hilfe/api.
    """

    # pylint: disable=duplicate-code  # overriding do_request is similar in every facade
    def do_request(
        self,
        method: http.HTTPMethod,
        url_path: str,
        *,
        content_type=MediaType.JSON,
        accept_type=None,
        **kwargs,
    ) -> requests.Response:
        return super().do_request(
            method,
            url_path,
            content_type=content_type,
            accept_type=accept_type,
            **kwargs,
        )

    def _do_paginated_request(
        self,
        method: http.HTTPMethod,
        url: str,
        *,
        page_args_path: tuple,
        content_identifier: str,
        params: dict | None = None,
        proxy_list: ProxyList | None = None,
        response_limit: t.Optional[int] = None,
        **kwargs,
    ) -> t.Iterator[dict]:
        """Helper to execute paginated request for REST API."""
        self.cursor: str | None = None

        def unpack_page(paged_response: requests.Response) -> Page:
            json_response = content = paged_response.json()
            content = json_response[content_identifier]
            new_cursor = json_response['cursor']
            has_next_page = self.cursor != new_cursor
            self.cursor = new_cursor
            if has_next_page:
                # return new cursor, and add new content
                return Page(new_cursor, content)
            # there is no new page, return none as now new cursor and [] as content is already in from last iteration
            return Page(None, [])

        def get_next_page_cursor(cursor: bool) -> PageCursor | None:
            if cursor:
                return PageCursor('cursor', cursor)
            return None

        yield from self.do_paginated_request(
            method,
            url,
            unpack_page=unpack_page,
            get_next_page_cursor=get_next_page_cursor,
            params=params,
            proxy_list=proxy_list,
            response_limit=response_limit,
            page_args_path=page_args_path,
            **kwargs,
        )

    @classmethod
    def get_instance(cls, configuration: Settings) -> t.Self:
        _logger.info('connecting to DIP Bundestag: %s', configuration.DIP_BUNDESTAG_BASE_URL)

        auth = Auth(
            auth_type=AuthType.DIPBUNDESTAG_API_TOKEN, token=configuration.DIP_BUNDESTAG_API_KEY
        )
        return cls(base_url=configuration.DIP_BUNDESTAG_BASE_URL, auth=auth)

    def get_drucksachen(
        self,
        since_datetime: str,
        response_limit: t.Optional[int] = None,
        proxy_list: ProxyList | None = None,
    ) -> t.Iterator[Drucksache]:
        """Get Drucksachen.
        https://search.dip.bundestag.de/api/v1/swagger-ui/#/Drucksachen/getDrucksacheList

        Args:
            since_datetime
                Updated later than since_date, in format YYYY-MM-DDTHH:mm:ss, e.g.2023-11-14T04:28:00.

        Returns:
            drucksachen (Iterator[Drucksache]):
                An iterator of Drucksache objects.
        """
        _logger.info("Fetching drucksachen.")

        for drucksache in self._do_paginated_request(
            http.HTTPMethod.GET,
            '/api/v1/drucksache',
            page_args_path=PAGINATION_CONTENT_ARGS_REST,
            content_identifier='documents',
            params={
                "f.aktualisiert.start": since_datetime,
            },
            response_limit=response_limit,
            proxy_list=proxy_list,
        ):
            yield Drucksache.model_validate(drucksache)

    def get_drucksachen_text(
        self,
        since_datetime: str,
        response_limit: t.Optional[int] = None,
        proxy_list: ProxyList | None = None,
    ) -> t.Iterator[DrucksacheText]:
        """Get Drucksachen-Text.
        https://search.dip.bundestag.de/api/v1/swagger-ui/#/Drucksachen/getDrucksacheTextList

        Args:
            since_datetime
                Updated later than since_date, in format YYYY-MM-DDTHH:mm:ss, e.g.2023-11-14T04:28:00.

        Returns:
            drucksachen_text (Iterator[DrucksacheText]): An iterator of DrucksacheText objects.
        """

        _logger.info("Fetching drucksachen.")

        for drucksache_text in self._do_paginated_request(
            http.HTTPMethod.GET,
            '/api/v1/drucksache-text',
            page_args_path=PAGINATION_CONTENT_ARGS_REST,
            content_identifier='documents',
            params={
                "f.aktualisiert.start": since_datetime,
            },
            response_limit=response_limit,
            proxy_list=proxy_list,
        ):
            yield DrucksacheText.model_validate(drucksache_text)

    def get_vorgange(
        self,
        since_datetime: str,
        response_limit: t.Optional[int] = None,
        proxy_list: ProxyList | None = None,
    ) -> t.Iterator[Vorgang]:
        """Get Vorgange.
        https://search.dip.bundestag.de/api/v1/swagger-ui/#/Vorg%C3%A4nge/getVorgangList

        Args:
            since_datetime
                Updated later than since_date, in format YYYY-MM-DDTHH:mm:ss, e.g.2023-11-14T04:28:00.

        Returns:
            vorgange (Iterator[DIPBundestagApiVorgang]):
                An iterator of DIPBundestagApiVorgang objects.
        """
        _logger.info("Fetching vorgange.")

        for vorgang in self._do_paginated_request(
            http.HTTPMethod.GET,
            '/api/v1/vorgang',
            page_args_path=PAGINATION_CONTENT_ARGS_REST,
            content_identifier='documents',
            params={
                "f.aktualisiert.start": since_datetime,
            },
            response_limit=response_limit,
        ):
            yield Vorgang.model_validate(vorgang)

    def get_vorgangsbezuege_of_plenarprotokoll_by_id(
        self, plenarprotokoll_id: int
    ) -> list[PlenarprotokollVorgangsbezug]:
        """Get vorgangsbezuege of a a given plenarprotokoll (by id).

        Required for getting content of plenarprotokoll, because vorgangsbezuege lists
        vorgangsbezuege with title and abstract information which will be leveraged for wordcloud
        analyzer.

        Args:
            plenarprotokoll_id (int): id of a plenarprotokoll

        Returns:
            list[PlenarprotokollVorgangsbezug]: list of PlenarprotokollVorgangsbezug objects, reduced to only relevant data needed.
        """

        _logger.info("Fetching vorgangsbezuege of plenaprotokoll with id %d.", plenarprotokoll_id)

        vorgangsbezuege_of_plenarprotokoll = [
            PlenarprotokollVorgangsbezug.model_validate(plenarprotokoll_vorgangsbezug)
            for plenarprotokoll_vorgangsbezug in self._do_paginated_request(
                http.HTTPMethod.GET,
                '/api/v1/vorgang',
                page_args_path=PAGINATION_CONTENT_ARGS_REST,
                content_identifier='documents',
                params={
                    "f.plenarprotokoll": plenarprotokoll_id,
                },
            )
        ]

        return vorgangsbezuege_of_plenarprotokoll

    def get_vorgangspositionen(
        self,
        since_datetime: str,
        response_limit: t.Optional[int] = None,
        proxy_list: ProxyList | None = None,
    ) -> t.Iterator[Vorgangsposition]:
        """Get Vorgangspositionen
        https://search.dip.bundestag.de/api/v1/swagger-ui/#/Vorgangspositionen/getVorgangspositionList

        Args:
            since_datetime
                Updated later than since_date, in format YYYY-MM-DDTHH:mm:ss, e.g.2023-11-14T04:28:00.

        Returns:
            vorgangsposition (Iterator[Vorgangsposition]):
                An iterator of Vorgangsposition objects.
        """
        _logger.info("Fetching vorgange.")

        for vorgangsposition in self._do_paginated_request(
            http.HTTPMethod.GET,
            '/api/v1/vorgangsposition',
            page_args_path=PAGINATION_CONTENT_ARGS_REST,
            content_identifier='documents',
            params={
                "f.aktualisiert.start": since_datetime,
            },
            response_limit=response_limit,
            proxy_list=proxy_list,
        ):
            yield Vorgangsposition.model_validate(vorgangsposition)

    def get_plenarprotokolle(
        self,
        date_start: datetime.date | None = None,
        date_end: datetime.date | None = None,
        wahlperiode: int | None = None,
        zuordnung: str | None = None,
        response_limit: int = 1000,
        proxy_list: ProxyList | None = None,
    ) -> t.Iterator[Plenarprotokoll]:
        """Get Plenarprotokolle.
        https://search.dip.bundestag.de/api/v1/swagger-ui/#/Plenarprotokolle/getPlenarprotokollList

        Args:
            wahlperiode (int):
                Number of wahlperiode, currently (2023) it is wahlperiode 20, which is also the default.
            zuordnung (str):
                Possible values are, BT, BR, BV, EK. Default is BT for Bundestag.
                (For now only the only part we are interested, that's why BT set as default.)
        Returns:
            plenarprotokolle (Iterator[Plenarprotokoll]):
                An iterator of Plenarprotokoll objects.

        """

        _logger.info("Get plenarprotkolle")

        for plenarprotokoll in self._do_paginated_request(
            http.HTTPMethod.GET,
            '/api/v1/plenarprotokoll',
            page_args_path=PAGINATION_CONTENT_ARGS_REST,
            content_identifier='documents',
            params={
                "f.zuordnung": zuordnung,
                "f.wahlperiode": wahlperiode,
                "f.datum.start": date_start,
                "f.datum.end": date_end,
            },
            response_limit=response_limit,
            proxy_list=proxy_list,
        ):
            yield Plenarprotokoll.model_validate(plenarprotokoll)

    def get_plenarprotokolle_text(
        self,
        wahlperiode: int = 20,
        zuordnung: str = "BT",
        response_limit: int = 1000,
        proxy_list: ProxyList | None = None,
    ) -> t.Iterator[PlenarprotokollText]:
        """Get Plenarprotokolle-Text.
        https://search.dip.bundestag.de/api/v1/swagger-ui/#/Plenarprotokolle/getPlenarprotokollTextList

        Args:
            wahlperiode (int):
                Number of wahlperiode, currently (2023) it is wahlperiode 20, which is also the default.
            zuordnung (str):
                Possible values are, BT, BR, BV, EK. Default is BT for Bundestag.
                (For now only the only part we are interested, that's why BT set as default.)
        Returns:
            plenarprotokolle_text (Iterator[PlenarprotokollText]):
                An iterator of Plenarprotokoll-Text objects.

        """

        _logger.info("Get plenarprotkolle-text")

        for plenarprotokoll_text in self._do_paginated_request(
            http.HTTPMethod.GET,
            '/api/v1/plenarprotokoll-text',
            page_args_path=PAGINATION_CONTENT_ARGS_REST,
            content_identifier='documents',
            params={
                "f.zuordnung": zuordnung,
                "f.wahlperiode": wahlperiode,
            },
            response_limit=response_limit,
            proxy_list=proxy_list,
        ):
            yield PlenarprotokollText.model_validate(plenarprotokoll_text)
