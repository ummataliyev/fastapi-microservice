"""
Module providing a configurable retry policy for async HTTP calls using tenacity.
"""

import httpx

from tenacity import retry
from tenacity import wait_exponential
from tenacity import stop_after_attempt
from tenacity import retry_if_exception_type


class AsyncHTTPRetry:
    """
    Configurable retry policy for async HTTP calls.

    :param attempts: Number of retry attempts.
    :param multiplier: Exponential backoff multiplier.
    :param min_wait: Minimum wait time between retries (seconds).
    :param max_wait: Maximum wait time between retries (seconds).
    :param retry_exceptions: Tuple of exception types that should trigger a retry.
    """

    def __init__(
        self,
        attempts: int = 3,
        multiplier: float = 0.5,
        min_wait: float = 1,
        max_wait: float = 5,
        retry_exceptions: tuple[type[Exception], ...] | None = None,
    ):
        self.attempts = attempts
        self.multiplier = multiplier
        self.min_wait = min_wait
        self.max_wait = max_wait
        self.retry_exceptions = retry_exceptions or (
            httpx.TimeoutException,
            httpx.ConnectError,
            httpx.ReadError,
        )

    def decorator(self):
        """
        Returns a tenacity retry decorator to be applied to async HTTP functions.

        :return: A tenacity retry decorator with exponential backoff.
        """
        return retry(
            stop=stop_after_attempt(self.attempts),
            wait=wait_exponential(
                multiplier=self.multiplier,
                min=self.min_wait,
                max=self.max_wait,
            ),
            retry=retry_if_exception_type(self.retry_exceptions),
            reraise=True,
        )
