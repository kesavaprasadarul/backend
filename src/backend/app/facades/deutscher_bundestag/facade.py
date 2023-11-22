"""DIP Bundestag facade."""
import http
import logging
import typing as t

import requests


from backend.app.core.config import Settings
from backend.app.facades.deutscher_bundestag.model import (
    Drucksache,
    Vorgang,
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

        return self.do_paginated_request(
            method,
            url,
            unpack_page=unpack_page,
            get_next_page_cursor=get_next_page_cursor,
            params=params,
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

    def get_drucksachen(self, since_datetime: str) -> list[Drucksache]:
        """Get Drucksachen.

        Args:
            since_datetime
                Updated later than since_date, in format YYYY-MM-DDTHH:mm:ss, e.g.2023-11-14T04:28:00.

        Returns:
            drucksachen (list[TServicedeskApiIssueType]):
                A list of TServicedeskApiIssueType objects.
        """
        _logger.info("Fetching plenarprotokolle.")

        drucksachen_unformatted = [
            drucksache
            for drucksache in self._do_paginated_request(
                http.HTTPMethod.GET,
                '/api/v1/drucksache',
                page_args_path=PAGINATION_CONTENT_ARGS_REST,
                content_identifier='documents',
                params={
                    "f.aktualisiert.start": since_datetime,
                },
            )
        ]

        for drucksache in drucksachen_unformatted:
            try:
                Drucksache.model_validate(drucksache)
            except Exception as e:
                print(e)
        # drucksachen = [
        #     DIPBundestagApiDrucksache.model_validate(drucksache)
        #     for drucksache in self._do_paginated_request(
        #         http.HTTPMethod.GET,
        #         '/api/v1/drucksache-text',
        #         page_args_path=PAGINATION_CONTENT_ARGS_REST,
        #         content_identifier='documents',
        #         params={
        #             "f.aktualisiert.start": since_datetime,
        #         },
        #     )
        # ]

        return drucksachen_unformatted

    def get_vorgang(self) -> list[Vorgang]:
        """Get Vorgang.

        Args:
            since_datetime
                Updated later than since_date, in format YYYY-MM-DDTHH:mm:ss, e.g.2023-11-14T04:28:00.

        Returns:
            vorgang (list[DIPBundestagApiVorgang]):
                A list of DIPBundestagApiVorgang objects.
        """
        _logger.info("Fetching vorgang.")

        vorgang = [
            Vorgang.model_validate(vorgang)
            for vorgang in self._do_paginated_request(
                http.HTTPMethod.GET,
                '/api/v1/vorgang',
                page_args_path=PAGINATION_CONTENT_ARGS_REST,
                content_identifier='documents',
            )
        ]

        return vorgang
