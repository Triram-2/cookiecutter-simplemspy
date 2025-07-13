from collections import defaultdict
from typing import Any, Dict, List, DefaultDict


class FakeRedisStream:
    """In-memory Redis Streams emulator."""

    def __init__(self) -> None:
        self.streams: DefaultDict[str, List[Dict[str, Any]]] = defaultdict(list)

    async def xadd(self, stream_name: str, fields: Dict[str, Any]) -> str:
        """Add a message to the specified stream."""
        self.streams[stream_name].append(fields)
        return str(len(self.streams[stream_name]))


TASKS_STREAM_NAME = "tasks:stream"

redis_stream = FakeRedisStream()

__all__ = ["redis_stream", "TASKS_STREAM_NAME", "FakeRedisStream"]
