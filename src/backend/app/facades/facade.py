"""HTTP facade."""

import collections.abc
import dataclasses
import enum
import http
import logging
import typing as t
import urllib.parse

import pydantic as pyd
import requests

from backend.app.core.config import Settings
from backend.app.facades.util import Proxy, ProxyList, call_with_retries

_logger = logging.getLogger(__name__)


LIMIT_PAGES = 10
"""Limit to getting only first 10 pages to not overstrain api of Deutscher Bundestag. Can be overwrriten."""

HTTP_REQUEST_DEFAULT_TIMEOUT_SECS = 30
"""Maximum time before an HTTP request times out."""


@dataclasses.dataclass
class Page:
    """Page of a paginated request with content consisting of the elements in current page."""

    page_info: t.Any
    content: t.Iterable[dict]


@dataclasses.dataclass
class PageSize:
    """Number of items returned by a paginated request per page."""

    name: str
    value: int


@dataclasses.dataclass
class PageCursor:
    """Next page to return by page paginated request."""

    name: str
    value: t.Any


PAGINATION_ARGS_REST = ('params',)
"""Pagination arguments specified as URL parameters, used in REST APIs."""

PAGINATION_CONTENT_ARGS_REST = ('json',)
"""Pagination arguments specified as content in the body, used in REST APIs."""


class AuthType(enum.Enum):
    DIPBUNDESTAG_API_TOKEN = enum.auto()
    TOKEN = enum.auto()
    BASIC_AUTHENTICATION = enum.auto()
    TOKEN_AS_USER = enum.auto()


class Auth(pyd.BaseModel):
    """The authentication method to be used."""

    auth_type: AuthType
    username: str | None = None
    password: str | None = None
    token: str | None = None


class MediaType(enum.Enum):
    JSON = 'application/json'


class HttpFacade:
    """Requests specific extension of the base facade.

    This class adds requests specific functionality by give a do request function which does all the
    magic and only needs the request specific parameters like url path and so on.
    """

    def __init__(self, base_url: str, auth: Auth):
        self.base_url = base_url
        self.auth = auth
        self._session = requests.Session()

    @classmethod
    def get_instance(cls, settings: Settings):
        raise NotImplementedError()

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

        proxy_dict = proxy.to_dict() if proxy else None

        if disable_retry:
            response = self._session.send(
                request=request,
                timeout=timeout,
                proxies=proxy_dict,
                verify=proxy is None,
                allow_redirects=False,
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

    def do_paginated_request(
        self,
        *args,
        unpack_page: t.Callable[[requests.Response], Page],
        get_next_page_cursor: t.Callable[[t.Any], t.Optional[PageCursor]],
        page_args_path: tuple[str, ...] = PAGINATION_ARGS_REST,
        params: t.Optional[dict],
        proxy_list: t.Optional[ProxyList] = None,
        response_limit: t.Optional[int] = None,
        **kwargs,
    ) -> collections.abc.Iterator[dict]:
        """Execute paginated http requests to external services.

        Preparation of a paginated request includes defining callables to unpack the response, get
        the next page and detect the last page. For this purpose paging info from the last response
        is given to the caller.

        Args:
            unpack_page:
                Function to unpack info about the page and its content. The content is expected to
                be an iterable of the elements received as part of the current page.

            get_next_page_cursor:
                Function to get the cursor of the next page or `None` if the last page is reached.

            page_size:
                Optional size of a page to customize default size defined by service.

            page_args_path:
                Path into the kwargs dictionary where the page information is stored.

            params:
                Optional params of request

            proxy_list:
                Optional proxy list to be used for the request.

            response_limit:
                Optional limit of requests to be executed. If not given, all pages are returned.

        Returns:
            Yields the unpacked content of each page.
        """
        page_args_dict = kwargs
        for name in page_args_path:
            page_args_dict = page_args_dict.setdefault(name, {})

        if params is None:
            params = {}

        reached_end = False
        while not reached_end and (response_limit is None or response_limit > 0):
            try:
                response = self.do_request(
                    *args,
                    **kwargs,
                    params=params,
                    proxy=proxy_list.get_proxy() if proxy_list else None,
                )
                response.raise_for_status()
            except (
                requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectionError,
            ) as e:
                if proxy_list:
                    print(f"Could not get response. Trying again with new proxy. Error: {e}")
                    proxy_list.set_random_proxy(test=True)
                    continue
                else:
                    raise e

            page = unpack_page(response)

            if isinstance(page.content, collections.abc.Sequence):
                yield from page.content
            else:
                raise NotImplementedError(f'Unexpected page content type {type(page.content)}.')

            if cursor := get_next_page_cursor(page.page_info):
                _logger.info(f'Next cursor: {cursor}.')
                params[cursor.name] = cursor.value
            else:
                _logger.info('Reached end of pages.')
                reached_end = True

            if response_limit is not None:
                response_limit -= 1
