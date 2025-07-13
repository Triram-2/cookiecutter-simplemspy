import asyncio
from collections import defaultdict
from typing import DefaultDict

from ..core.config import settings


class AsyncStatsDClient:
    """Very small async StatsD client using UDP."""

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.counters: DefaultDict[str, int] = defaultdict(int)

    async def _send(self, message: bytes) -> None:
        loop = asyncio.get_running_loop()
        transport, _ = await loop.create_datagram_endpoint(
            lambda: asyncio.DatagramProtocol(), remote_addr=(self.host, self.port)
        )
        transport.sendto(message)
        transport.close()

    async def incr(self, metric: str, value: int = 1) -> None:
        self.counters[metric] += value
        msg = f"{metric}:{value}|c".encode()
        try:
            await self._send(msg)
        except Exception:
            # Metrics should never crash the app
            pass

    def reset(self) -> None:
        self.counters.clear()


statsd_client = AsyncStatsDClient(settings.statsd.host, settings.statsd.port)

__all__ = ["AsyncStatsDClient", "statsd_client"]
