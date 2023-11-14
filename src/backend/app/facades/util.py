"""Facade util functions."""
import contextlib
import logging
import time
import traceback
import typing as t

import requests


_logger = logging.getLogger(__name__)

ATTEMPT_AFTER_SECONDS = (0, 30, 60)
"""Number of seconds to wait before next attempt to call with retries."""


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
def catch_and_report_request_exception(
    error_message, error_type, reporter
):
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



def get_http_exception_text(exc: Exception) -> str | None:
    """Returns the response text if the given exception contains one."""
    if (response := getattr(exc, 'response', None)) is not None:
        if (text := getattr(response, 'text', None)) is not None:
            return text
    return None
