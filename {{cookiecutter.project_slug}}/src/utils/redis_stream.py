from typing import Any, Dict

from redis.asyncio import Redis

from ..core.config import settings


class RedisStream:
    """Async wrapper around Redis streams."""

    def __init__(self, url: str) -> None:
        self.redis = Redis.from_url(url, decode_responses=True)

    async def xadd(self, stream_name: str, fields: Dict[str, Any]) -> str:
        return await self.redis.xadd(
            stream_name, fields, maxlen=settings.redis.max_length
        )


TASKS_STREAM_NAME = settings.redis.stream_name

redis_stream = RedisStream(settings.redis.url)

__all__ = ["redis_stream", "TASKS_STREAM_NAME", "RedisStream"]
