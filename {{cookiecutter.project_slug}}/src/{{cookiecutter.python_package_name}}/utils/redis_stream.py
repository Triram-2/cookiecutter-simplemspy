"""Thin wrapper around Redis Stream operations."""

from typing import Any, Dict, cast

from redis.asyncio import Redis

from ..core.config import settings


class RedisStream:
    """Async wrapper around Redis streams."""

    def __init__(self, url: str) -> None:
        self.redis = Redis.from_url(url, decode_responses=True)

    async def xadd(self, stream_name: str, fields: Dict[str, Any]) -> str:
        result = await self.redis.xadd(
            stream_name,
            fields,
            maxlen=settings.redis.max_length,
        )
        return cast(str, result)

    async def ping(self) -> bool:
        """Check if Redis connection is alive."""
        result = await self.redis.ping()
        return cast(bool, result)


TASKS_STREAM_NAME = settings.redis.stream_name

redis_stream = RedisStream(settings.redis.url)

__all__ = ["TASKS_STREAM_NAME", "RedisStream", "redis_stream"]
