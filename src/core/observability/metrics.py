"""
Prometheus metrics registry and helpers.
"""

try:
    from prometheus_client import Counter
    from prometheus_client import Histogram
    from prometheus_client import generate_latest
    from prometheus_client import CONTENT_TYPE_LATEST
except ImportError:  # pragma: no cover
    class _NoopMetric:
        """
        _NoopMetric class.
        :raises Exception: If class initialization or usage fails.
        """
        def labels(self, **kwargs):  # noqa: ARG002
            """
            Labels.

            :param kwargs: TODO - describe kwargs.
            :return: TODO - describe return value.
            :raises Exception: If the operation fails.
            """
            return self

        def inc(self, amount: float = 1.0):  # noqa: ARG002
            """
            Inc.

            :param amount: TODO - describe amount.
            :type amount: float
            :return: None.
            :raises Exception: If the operation fails.
            """
            return None

        def observe(self, amount: float):  # noqa: ARG002
            """
            Observe.

            :param amount: TODO - describe amount.
            :type amount: float
            :return: None.
            :raises Exception: If the operation fails.
            """
            return None

    Counter = Histogram = lambda *args, **kwargs: _NoopMetric()

    def generate_latest() -> bytes:
        """
        Generate latest.

        :return: TODO - describe return value.
        :rtype: bytes
        :raises Exception: If the operation fails.
        """
        return b""

    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4; charset=utf-8"


HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total number of HTTP requests.",
    ["method", "path", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "Request latency in seconds.",
    ["method", "path"],
)


def render_metrics() -> tuple[bytes, str]:
    """
    Render metrics.

    :return: TODO - describe return value.
    :rtype: tuple[bytes, str]
    :raises Exception: If the operation fails.
    """
    return generate_latest(), CONTENT_TYPE_LATEST
