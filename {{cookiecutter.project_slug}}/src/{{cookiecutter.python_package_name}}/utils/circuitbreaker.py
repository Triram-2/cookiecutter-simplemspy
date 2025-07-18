from __future__ import annotations

"""Simple asynchronous circuit breaker implementation."""

from datetime import datetime, timedelta
from typing import Awaitable, Callable, TypeVar




class CircuitBreakerError(Exception):
    """Raised when the circuit is open."""


T = TypeVar("T")


class CircuitBreaker:
    """Minimal async circuit breaker."""

    def __init__(self, fail_max: int, timeout_duration: timedelta) -> None:
        self.fail_max = fail_max
        self.timeout_duration = timeout_duration
        self._failure_count = 0
        self._opened_until: datetime | None = None

    async def call_async(
        self, func: Callable[..., Awaitable[T]], *args: object, **kwargs: object
    ) -> T:
        if self._opened_until and datetime.now() < self._opened_until:
            raise CircuitBreakerError("circuit breaker is open")

        try:
            result = await func(*args, **kwargs)
        except Exception as exc:
            self._failure_count += 1
            if self._failure_count >= self.fail_max:
                self._opened_until = datetime.now() + self.timeout_duration
                self._failure_count = 0
                raise CircuitBreakerError("circuit breaker is open") from exc
            raise
        else:
            self._failure_count = 0
            self._opened_until = None
            return result


__all__ = ["CircuitBreaker", "CircuitBreakerError"]
