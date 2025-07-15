"""Thin wrapper around Redis Stream operations."""

# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportArgumentType=false

from typing import Any, Dict, cast

from redis.asyncio import Redis  # pyright: ignore[reportMissingImports]

from ..core.config import settings


class RedisStream:
    """Async wrapper around Redis streams."""

    def __init__(self, url: str) -> None:
        self.redis: Redis = Redis.from_url(url, decode_responses=True)  # pyright: ignore[reportUnknownMemberType,reportInvalidTypeArguments]

    async def xadd(self, stream_name: str, fields: Dict[str, Any]) -> str:
        result: Any = await self.redis.xadd(
            stream_name, fields, maxlen=settings.redis.max_length
        )  # pyright: ignore[reportUnknownMemberType]
        return cast(str, result)

    async def ping(self) -> bool:
        """Check if Redis connection is alive."""
        result: Any = await self.redis.ping()  # pyright: ignore[reportUnknownMemberType]
        return cast(bool, result)


TASKS_STREAM_NAME = settings.redis.stream_name

redis_stream = RedisStream(settings.redis.url)

__all__ = ["TASKS_STREAM_NAME", "RedisStream", "redis_stream"]
