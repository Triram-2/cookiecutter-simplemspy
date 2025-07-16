"""Utility helpers for the application."""

from ..core.config import settings
from .metrics import statsd_client
from .redis_stream import RedisStream, TASKS_STREAM_NAME, redis_stream
from .tracing import tracer
from .circuitbreaker import CircuitBreaker, CircuitBreakerError

__all__ = [
    "TASKS_STREAM_NAME",
    "RedisStream",
    "redis_stream",
    "TASKS_ENDPOINT_PATH",
    "statsd_client",
    "tracer",
    "CircuitBreaker",
    "CircuitBreakerError",
]

TASKS_ENDPOINT_PATH = settings.service.tasks_endpoint
