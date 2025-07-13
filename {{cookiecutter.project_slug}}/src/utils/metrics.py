from collections import defaultdict
from typing import DefaultDict

class StatsDClient:
    """Simplified in-memory StatsD client."""

    def __init__(self) -> None:
        self.counters: DefaultDict[str, int] = defaultdict(int)

    def incr(self, metric: str, value: int = 1) -> None:
        self.counters[metric] += value

    def reset(self) -> None:
        self.counters.clear()

statsd_client = StatsDClient()

__all__ = ["statsd_client", "StatsDClient"]
