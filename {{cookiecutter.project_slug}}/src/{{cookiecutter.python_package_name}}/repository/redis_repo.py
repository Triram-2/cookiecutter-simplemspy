from __future__ import annotations
# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportArgumentType=false

"""Redis repository used for queue operations."""

from datetime import timedelta
from typing import Any, Awaitable, Callable, Dict, cast

from ..utils import CircuitBreaker, tracer

from redis.asyncio import Redis

from ..core.config import settings


class RedisRepository:
    """Wrapper around Redis operations used by the service."""

    def __init__(
        self, client: Redis | None = None, url: str = settings.redis.url
    ) -> None:
        self.redis = client or Redis.from_url(url, decode_responses=True)  # pyright: ignore[reportUnknownMemberType]
        self.breaker: CircuitBreaker = CircuitBreaker(
            fail_max=settings.redis.breaker_fail_max,
            timeout_duration=timedelta(seconds=settings.redis.breaker_reset_timeout),
        )

    async def add_to_stream(self, stream_name: str, message: Dict[str, Any]) -> str:
        """Add a message to a Redis Stream."""
        with tracer.start_as_current_span("добавление_в_redis_стрим"):
            result: Any = await self.breaker.call_async(
                cast(Callable[..., Awaitable[Any]], self.redis.xadd),
                stream_name,
                message,
                maxlen=settings.redis.max_length,
            )
            return cast(str, result)

    async def ping(self) -> bool:
        """Check Redis connectivity."""
        with tracer.start_as_current_span("пинг_redis"):
            result: Any = await self.breaker.call_async(
                cast(Callable[..., Awaitable[Any]], self.redis.ping)
            )
            return cast(bool, result)


__all__ = ["RedisRepository"]
