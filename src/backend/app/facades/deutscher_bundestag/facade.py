"""DIP Bundestag facade."""
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
from backend.app.facades.deutscher_bundestag.parameter_model import (
    DrucksacheParameter,
    PlenarprotokollParameter,
    VorgangParameter,
    VorgangspositionParameter,
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
    HTTP_REQUEST_DEFAULT_TIMEOUT_SECS,
)
from backend.app.facades.util import ProxyList, Proxy, call_with_retries
import urllib.parse

_logger = logging.getLogger(__name__)


PAGE_SIZE = 100
"""Number of elements returned in a single paged response."""


class DIPBundestagFacade(HttpFacade):
    """Facade implementation for a DIP Bundestag.

    For more information look at docu of DIP bundestag API:
    https://dip.bundestag.de/%C3%BCber-dip/hilfe/api.
    """

    # TODO: Sometimes the API redirects and expectes some javascript execution
    # Potentially this is just a sha256-post which we could mock (maybe here)
    # hence why I pulled out this session sending into a separate method
    def _send_request(
        self,
        request: requests.PreparedRequest,
        timeout: int,
        proxies: t.Optional[dict[str, str]] = None,
        verify: bool = True,
    ) -> requests.Response:
        response = self._session.send(
            request=request,
            timeout=timeout,
            proxies=proxies,
            verify=verify,
        )

        return response

    # pylint: disable=duplicate-code  # overriding do_request is similar in every facade
    def do_request(
        self,
        method: http.HTTPMethod,
        url_path: str,
        *,
        content_type: t.Optional[MediaType] = None,
        accept_type: t.Optional[MediaType] = None,
        final_http_codes: t.Optional[set[int]] = None,
        retry_http_codes: t.Optional[set[int]] = None,
        json: t.Optional[dict] = None,
        data: t.Optional[str] = None,
        params: t.Optional[dict] = None,
        headers: t.Optional[dict] = None,
        proxy: t.Optional[Proxy] = None,
        timeout: int = HTTP_REQUEST_DEFAULT_TIMEOUT_SECS,
        disable_retry: bool = False,
    ) -> requests.Response:
        """Execute http requests to external services.

        Preparation of a request includes setting mandatory standard headers, setting auth header
        and calculating the final target url based on the endpoint url. For performance reasons, a
        requests Session is used internally.

        In case the request fails, the method will attempt to retry. By default, only HTTP codes >=
        500 will be reattempted. Use ``final_http_codes`` and ``retry_http_codes`` to modify this
        behavior.

        Args:
            method: The http verb which should be used for the request.
            url_path: The path of the url, added to the hostname of the instance.
            content_type: The content type to be passed as header or None if no body is sent.
            accept_type: The accept type to be passed as header.
            json: A dict which will be passed as json.
            data: A string with data passed as part of the request.
            params: Query parameters which are added to the url.
            headers: headers of the request. Authorization and Accept are set by decorator.
            proxy: Optional proxy to be used for the request.
            final_http_codes: Additional http return codes which will not be retried.
            retry_http_codes: Additional http return codes which will be retried.
            timeout: Optional timeout value to change the default set in HTTP_REQUEST_TIMEOUT_SECS
            disable_retry: Optional flag to disable any retry in case of failures with default False
        Returns:
            The response of the request

        """
        all_headers = headers.copy() if headers else {}
        basic_auth = None

        match self.auth.auth_type:
            case AuthType.DIPBUNDESTAG_API_TOKEN:
                all_headers['Authorization'] = f'ApiKey {self.auth.token}'
            case AuthType.TOKEN:
                all_headers['Authorization'] = f'Bearer {self.auth.token}'
            case AuthType.BASIC_AUTHENTICATION:
                basic_auth = (
                    self.auth.username,
                    self.auth.password,
                )
            case AuthType.TOKEN_AS_USER:
                basic_auth = (self.auth.token, '')
            case _:  # pragma: no cover  # coverage.py does not recognize pattern
                raise NotImplementedError(self.auth.auth_type)

        if content_type:
            all_headers['Content-Type'] = content_type.value

        if accept_type:
            all_headers['Accept'] = accept_type.value

        request = requests.Request(
            method=method.value,
            url=urllib.parse.urljoin(self.base_url, url_path),
            params=params,
            headers=all_headers,
            json=json,
            data=data,
            auth=basic_auth,
        ).prepare()

        def is_response_final(r: requests.Response) -> bool:
            """Return if response is final, i.e. request should not be retried."""

            if final_http_codes and r.status_code in final_http_codes:
                return True

            if retry_http_codes and r.status_code in retry_http_codes:
                return False

            return r.status_code < 500

        proxy_dict = (
            {
                'http': f'http://{proxy.url}',
            }
            if proxy
            else None
        )

        if disable_retry:
            response = self._send_request(
                request=request,
                timeout=timeout,
                proxies=proxy_dict,
                verify=proxy is None,
            )
        else:
            response = call_with_retries(
                self._session.send,
                request,
                retval_ok=is_response_final,
                timeout=timeout,
                proxies=proxy_dict,
                verify=proxy is None,
            )

        return response

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
        params: DrucksacheParameter | None = None,
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

        param_dict = (
            params.model_dump(mode='json', exclude_none=True, by_alias=True) if params else None
        )

        for drucksache in self._do_paginated_request(
            http.HTTPMethod.GET,
            '/api/v1/drucksache',
            page_args_path=PAGINATION_CONTENT_ARGS_REST,
            content_identifier='documents',
            params=param_dict,
            response_limit=response_limit,
            proxy_list=proxy_list,
        ):
            yield Drucksache.model_validate(drucksache)

    def get_drucksachen_text(
        self,
        params: DrucksacheParameter | None = None,
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

        param_dict = (
            params.model_dump(mode='json', exclude_none=True, by_alias=True) if params else None
        )

        _logger.info("Fetching drucksachen-text with params %s.", param_dict)

        for drucksache_text in self._do_paginated_request(
            http.HTTPMethod.GET,
            '/api/v1/drucksache-text',
            page_args_path=PAGINATION_CONTENT_ARGS_REST,
            content_identifier='documents',
            params=param_dict,
            response_limit=response_limit,
            proxy_list=proxy_list,
        ):
            yield DrucksacheText.model_validate(drucksache_text)

    def get_vorgange(
        self,
        params: VorgangParameter | None = None,
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
        param_dict = (
            params.model_dump(mode='json', exclude_none=True, by_alias=True) if params else None
        )

        _logger.info("Fetching vorgaenge with params %s.", param_dict)

        for vorgang in self._do_paginated_request(
            http.HTTPMethod.GET,
            '/api/v1/vorgang',
            page_args_path=PAGINATION_CONTENT_ARGS_REST,
            content_identifier='documents',
            params=param_dict,
            response_limit=response_limit,
            proxy_list=proxy_list,
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
        params: VorgangspositionParameter | None = None,
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
        param_dict = (
            params.model_dump(mode='json', exclude_none=True, by_alias=True) if params else None
        )

        _logger.info("Fetching vorgangspositionen with params %s.", param_dict)

        for vorgangsposition in self._do_paginated_request(
            http.HTTPMethod.GET,
            '/api/v1/vorgangsposition',
            page_args_path=PAGINATION_CONTENT_ARGS_REST,
            content_identifier='documents',
            params=param_dict,
            response_limit=response_limit,
            proxy_list=proxy_list,
        ):
            yield Vorgangsposition.model_validate(vorgangsposition)

    def get_plenarprotokolle(
        self,
        params: PlenarprotokollParameter | None = None,
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

        param_dict = (
            params.model_dump(mode='json', exclude_none=True, by_alias=True) if params else None
        )

        _logger.info("Fetching plenarprotokoll with params %s.", param_dict)

        for plenarprotokoll in self._do_paginated_request(
            http.HTTPMethod.GET,
            '/api/v1/plenarprotokoll',
            page_args_path=PAGINATION_CONTENT_ARGS_REST,
            content_identifier='documents',
            params=param_dict,
            response_limit=response_limit,
            proxy_list=proxy_list,
        ):
            yield Plenarprotokoll.model_validate(plenarprotokoll)

    def get_plenarprotokolle_text(
        self,
        params: PlenarprotokollParameter | None = None,
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

        param_dict = (
            params.model_dump(mode='json', exclude_none=True, by_alias=True) if params else None
        )

        _logger.info("Fetching plenarprotokoll-text with params %s.", param_dict)

        for plenarprotokoll_text in self._do_paginated_request(
            http.HTTPMethod.GET,
            '/api/v1/plenarprotokoll-text',
            page_args_path=PAGINATION_CONTENT_ARGS_REST,
            content_identifier='documents',
            params=param_dict,
            response_limit=response_limit,
            proxy_list=proxy_list,
        ):
            yield PlenarprotokollText.model_validate(plenarprotokoll_text)
