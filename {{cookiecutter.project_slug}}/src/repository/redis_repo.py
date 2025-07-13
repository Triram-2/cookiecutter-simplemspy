from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict, Optional

import aiobreaker

from redis.asyncio import Redis

from ..core.config import settings


class RedisRepository:
    """Wrapper around Redis operations used by the service."""

    def __init__(
        self, client: Optional[Redis] = None, url: str = settings.redis.url
    ) -> None:
        self.redis = client or Redis.from_url(url, decode_responses=True)
        self.breaker = aiobreaker.CircuitBreaker(
            fail_max=settings.redis.breaker_fail_max,
            timeout_duration=timedelta(seconds=settings.redis.breaker_reset_timeout),
        )

    async def add_to_stream(self, stream_name: str, message: Dict[str, Any]) -> str:
        """Add a message to a Redis Stream."""
        return await self.breaker.call_async(
            self.redis.xadd, stream_name, message, maxlen=settings.redis.max_length
        )

    async def ping(self) -> bool:
        """Check Redis connectivity."""
        return await self.breaker.call_async(self.redis.ping)


__all__ = ["RedisRepository"]
