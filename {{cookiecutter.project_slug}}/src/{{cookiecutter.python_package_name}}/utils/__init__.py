"""Utility helpers for the application."""

from ..core.config import settings
from .metrics import statsd_client
from .redis_stream import (
    DEAD_LETTER_STREAM_NAME,
    RedisStream,
    TASKS_STREAM_NAME,
    redis_stream,
)
from .tracing import tracer
from .circuitbreaker import CircuitBreaker, CircuitBreakerError

__all__ = [
    "CircuitBreaker",
    "CircuitBreakerError",
    "DEAD_LETTER_STREAM_NAME",
    "RedisStream",
    "TASKS_ENDPOINT_PATH",
    "TASKS_STREAM_NAME",
    "redis_stream",
    "statsd_client",
    "tracer",
]

TASKS_ENDPOINT_PATH = settings.service.tasks_endpoint
