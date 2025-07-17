from __future__ import annotations
# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportArgumentType=false

"""Redis repository used for queue operations."""

from datetime import timedelta
from typing import Any, Awaitable, Callable, Dict, List, Tuple, cast

from redis.exceptions import ResponseError

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

    async def create_group(self, stream_name: str) -> None:
        """Create consumer group if it does not exist."""
        with tracer.start_as_current_span("создание_группы"):
            try:
                await self.breaker.call_async(
                    cast(Callable[..., Awaitable[Any]], self.redis.xgroup_create),
                    stream_name,
                    settings.redis.consumer_group,
                    id="$",
                    mkstream=True,
                )
            except ResponseError as exc:
                if "BUSYGROUP" not in str(exc):
                    raise

    async def fetch(
        self, stream_name: str, count: int = 1, block_ms: int = 1000
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """Read messages from a stream using XREADGROUP."""
        with tracer.start_as_current_span("чтение_из_группы"):
            result: Any = await self.breaker.call_async(
                cast(Callable[..., Awaitable[Any]], self.redis.xreadgroup),
                settings.redis.consumer_group,
                settings.redis.consumer_name,
                streams={stream_name: ">"},
                count=count,
                block=block_ms,
            )
            messages: List[Tuple[str, Dict[str, Any]]] = []
            for _stream, msgs in result or []:
                for msg_id, data in msgs:
                    messages.append((cast(str, msg_id), cast(Dict[str, Any], data)))
            return messages

    async def ack(self, stream_name: str, message_id: str) -> int:
        """Acknowledge message processing."""
        with tracer.start_as_current_span("подтверждение"):
            result: Any = await self.breaker.call_async(
                cast(Callable[..., Awaitable[Any]], self.redis.xack),
                stream_name,
                settings.redis.consumer_group,
                message_id,
            )
            return cast(int, result)


__all__ = ["RedisRepository"]
