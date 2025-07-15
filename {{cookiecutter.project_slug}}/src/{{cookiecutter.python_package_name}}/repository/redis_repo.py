from __future__ import annotations

"""Redis repository used for queue operations."""

from datetime import timedelta
from typing import Any, Dict, cast

import aiobreaker

from redis.asyncio import Redis

from ..core.config import settings


class RedisRepository:
    """Wrapper around Redis operations used by the service."""

    def __init__(self, client: Redis | None = None, url: str = settings.redis.url) -> None:
        # Redis.from_url may lack type hints in some versions
        self.redis = client or Redis.from_url(url, decode_responses=True)  # pyright: ignore[reportUnknownMemberType]
        self.breaker: aiobreaker.CircuitBreaker[Any] = aiobreaker.CircuitBreaker(
            fail_max=settings.redis.breaker_fail_max,
            timeout_duration=timedelta(seconds=settings.redis.breaker_reset_timeout),
        )

    async def add_to_stream(self, stream_name: str, message: Dict[str, Any]) -> str:
        """Add a message to a Redis Stream."""
        result = await self.breaker.call_async(
            self.redis.xadd,
            stream_name,
            message,
            maxlen=settings.redis.max_length,
        )
        return cast(str, result)

    async def ping(self) -> bool:
        """Check Redis connectivity."""
        result = await self.breaker.call_async(self.redis.ping)
        return cast(bool, result)


__all__ = ["RedisRepository"]
