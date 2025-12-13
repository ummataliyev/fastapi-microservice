"""
Circuit breaker factory for downstream services.
"""

import pybreaker


class CircuitBreakerFactory:
    """
    Factory for creating circuit breakers per downstream service.

    :param fail_max: Maximum number of failures before opening the circuit breaker.
    :param reset_timeout: Time in seconds to wait before resetting the circuit breaker.
    """

    def __init__(
        self,
        fail_max: int = 5,
        reset_timeout: int = 30,
    ):
        self.fail_max = fail_max
        self.reset_timeout = reset_timeout
        self._breakers: dict[str, pybreaker.CircuitBreaker] = {}

    def get(self, service_name: str) -> pybreaker.CircuitBreaker:
        """
        Get or create a circuit breaker for a given service.

        Ensures one breaker per service name.

        :param service_name: Name of the downstream service.
        :return: An instance of `pybreaker.CircuitBreaker` for the specified service.
        """
        if service_name not in self._breakers:
            self._breakers[service_name] = pybreaker.CircuitBreaker(
                fail_max=self.fail_max,
                reset_timeout=self.reset_timeout,
                name=service_name,
            )
        return self._breakers[service_name]
