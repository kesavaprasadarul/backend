"""Facade util functions."""
import contextlib
import logging
import random
import time
import traceback
import typing as t

import pydantic as pyd
import requests

_logger = logging.getLogger(__name__)

ATTEMPT_AFTER_SECONDS = (0, 15, 30)
"""Number of seconds to wait before next attempt to call with retries."""


class ProxyListEmptyError(Exception):
    """Raised when proxy list is empty."""


class Proxy(pyd.BaseModel):
    """The proxy to be used."""

    url: str


class ProxyList:
    """The list of proxies to be used."""

    original_proxies: list[Proxy]
    proxies: list[Proxy]

    current_proxy: Proxy | None = None

    def __init__(self, proxies: list[Proxy]):
        self.original_proxies = proxies.copy()
        self.proxies = proxies.copy()

    def set_random_proxy(self, drop_previous: bool = True):
        """Get a randomly sampled proxy from the list."""

        if len(self.proxies) == 0:
            raise ProxyListEmptyError('No proxies available.')

        if drop_previous and self.current_proxy:
            self.proxies.remove(self.current_proxy)

        self.current_proxy = random.choice(self.proxies)

    def get_proxy(self) -> Proxy:
        """Get the current proxy from the list."""
        if self.current_proxy:
            return self.current_proxy

        self.set_random_proxy()

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
    def from_url(cls, proxy_url: str) -> t.Self:
        """Get a proxy list instance from a url."""
        proxies = []
        with requests.get(proxy_url) as response:
            for line in response.iter_lines():
                if line:
                    proxies.append(Proxy(url=line.decode('utf-8')))
        return cls(proxies)


def call_with_retries(
    callable_: t.Callable,
    *args,
    retval_ok: t.Callable[[t.Any], bool] = lambda _: True,
    **kwargs,
):
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
