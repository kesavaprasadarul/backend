"""Facade util functions."""
import contextlib
import logging
import random
import time
import traceback
import typing as t
from enum import Enum

import pydantic as pyd
import requests

_logger = logging.getLogger(__name__)

ATTEMPT_AFTER_SECONDS = (0, 15, 30)
"""Number of seconds to wait before next attempt to call with retries."""


class ProxyListEmptyError(Exception):
    """Raised when proxy list is empty."""


class ProxyMethod(Enum):
    """Proxy methods."""

    SOCKS4 = 'socks4'
    SOCKS5 = 'socks5'
    HTTP = 'http'


class Proxy(pyd.BaseModel):
    """The proxy to be used."""

    ip: str
    method: ProxyMethod = ProxyMethod.SOCKS5

    def to_dict(self) -> dict[str, str]:
        """Convert proxy to dict."""
        url_prefix = f'{self.method.value}://'

        return {
            'http': url_prefix + self.ip,
            'https': url_prefix + self.ip,
        }


class ProxyList:
    """The list of proxies to be used."""

    original_proxies: list[Proxy]
    proxies: list[Proxy]

    current_proxy: Proxy | None = None

    sample_test_domains: list[str] = ["www.google.com", "dip.bundestag.de"]

    def __init__(self, proxies: list[Proxy]):
        self.original_proxies = proxies.copy()
        self.proxies = proxies.copy()

    # from https://github.com/TheSpeedX/socker/blob/master/proxy_tester_menu.py
    def _test_proxy(self, domain: str, proxy: Proxy) -> bool:
        """Test a proxy."""
        proxies = proxy.to_dict()

        with contextlib.suppress(requests.RequestException):
            print(f"Testing https://{domain}, proxy: {proxies}")
            response = requests.get(f"http://{domain}", proxies=proxies, timeout=10, verify=False)
            if response.status_code >= 200 and response.status_code < 300:
                return True
        return False

    def test_sample_domains(self, proxy: Proxy) -> bool:
        for domain in self.sample_test_domains:
            if not self._test_proxy(domain, proxy):
                return False
        return True

    def set_random_proxy(self, drop_previous: bool = True, test: bool = True):
        """Get a randomly sampled proxy from the list and test if it works."""

        if len(self.proxies) == 0:
            raise ProxyListEmptyError('No proxies available.')

        if drop_previous and self.current_proxy:
            self.proxies.remove(self.current_proxy)

        new_proxy = random.choice(self.proxies)

        while test and not self.test_sample_domains(new_proxy):
            print(f"Proxy {new_proxy} failed test, removing from list.")
            self.proxies.remove(new_proxy)
            new_proxy = random.choice(self.proxies)
        print(f"Proxy {new_proxy} passed test.")
        self.current_proxy = new_proxy

    def get_proxy(self, test: bool = True) -> Proxy:
        """Get the current proxy from the list."""
        if self.current_proxy:
            return self.current_proxy

        self.set_random_proxy(test=test)

        if not self.current_proxy:
            raise ProxyListEmptyError('No proxy available.')

        return self.current_proxy

    def __len__(self) -> int:
        """Get the length of the list."""
        return len(self.proxies)

    def __getitem__(self, index: int) -> Proxy:
        """Get a proxy from the list."""
        return self.proxies[index]

    @classmethod
    def from_url(cls, proxy_url: str, method: ProxyMethod = ProxyMethod.SOCKS5) -> t.Self:
        """Get a proxy list instance from a url."""
        proxies = []
        with requests.get(proxy_url) as response:
            for line in response.iter_lines():
                if line:
                    proxies.append(Proxy(ip=line.decode('utf-8'), method=method))
        return cls(proxies)


R = t.TypeVar('R')


def call_with_retries(
    callable_: t.Callable[..., R],
    *args,
    retval_ok: t.Callable[[t.Any], bool] = lambda _: True,
    **kwargs,
) -> R:
    """Invoke a callable robustly with delayed retries.

    Failure of the invoked callable is indicated by a raised exception or if the return code does
    not pass the optional `retval_ok` predicate. If all retries failed, either the last erroneous
    return code or the last exception is propagated to caller.

    Args:
        callable_: Callable to be invoked with retries.
        retval_ok: Optional evaluation function indicating that the return value is OK.
        args: Optional positional arguments passed to callable.
        kwargs: Optional keyword arguments passed to callable.

    Returns:
        Last returned value of the callable.
    """
    num_attempts = len(ATTEMPT_AFTER_SECONDS)

    for attempt, delay in enumerate(ATTEMPT_AFTER_SECONDS, start=1):
        try:
            time.sleep(delay)
            retval = callable_(*args, **kwargs)

            if retval_ok(retval):
                # successful invocation, just propagate result:
                return retval

            _logger.warning(
                'Attempt %d failed, %d left. Return value: %r',
                attempt,
                num_attempts - attempt,
                retval,
            )

            if attempt >= num_attempts:
                _logger.error('All attempts failed.')
                return retval
        except requests.exceptions.ProxyError as ex:
            text = get_http_exception_text(ex)
            _logger.warning(
                'Attempt failed due to proxy error, %d left. %s: %s',
                attempt,
                num_attempts - attempt,
                type(ex).__name__,
                f'{ex}\n{text}' if text else ex,
            )
            raise
        # want to catch all other exceptions but also print it to log:
        except Exception as ex:  # pylint: disable=broad-except  # catch-all clause intended
            text = get_http_exception_text(ex)
            _logger.warning(
                'Attempt %d failed, %d left. %s: %s',
                attempt,
                num_attempts - attempt,
                type(ex).__name__,
                f'{ex}\n{text}' if text else ex,
            )
            if attempt >= num_attempts:
                _logger.error('All attempts failed.')
                raise

    # this is never reached, but make pylint happy:
    raise NotImplementedError()


@contextlib.contextmanager
def catch_and_report_request_exception(error_message, error_type, reporter):
    """Context manager that will catch requests' exceptions and report them."""

    try:
        yield
    except requests.RequestException as exc:
        complete_message = f'{error_message} {type(exc).__name__} - {str(exc)}'
        reporter.report_error(_logger, error_type=error_type, message=complete_message)
        log_response_body(exc)

        # send trace only to log (not reporter) for debugging:
        _logger.error(traceback.format_exc())


def log_response_body(exception: requests.RequestException, log_level: int = logging.ERROR):
    if text := get_http_exception_text(exception):
        _logger.log(log_level, 'HTTP response body: %s', text)


def get_http_exception_text(exc: Exception) -> str | None | t.Any:
    """Returns the response text if the given exception contains one."""
    if (response := getattr(exc, 'response', None)) is not None:
        if (text := getattr(response, 'text', None)) is not None:
            return text
    return None
