"""Simple asynchronous StatsD client."""

import asyncio
from collections import defaultdict
from typing import DefaultDict

from ..core.config import settings


class AsyncStatsDClient:
    """Very small async StatsD client using UDP."""

    def __init__(self, host: str, port: int, prefix: str = "") -> None:
        """Initialize the client."""
        self.host = host
        self.port = port
        self.prefix = prefix
        self.counters: DefaultDict[str, int] = defaultdict(int)
        self.gauges: DefaultDict[str, float] = defaultdict(float)
        self._transport: asyncio.DatagramTransport | None = None

    def _format(self, metric: str) -> str:
        return f"{self.prefix}.{metric}" if self.prefix else metric

    async def _ensure_transport(self) -> None:
        if self._transport is None:
            loop = asyncio.get_running_loop()
            self._transport, _ = await loop.create_datagram_endpoint(
                lambda: asyncio.DatagramProtocol(), remote_addr=(self.host, self.port)
            )

    async def _send(self, message: bytes) -> None:
        """Send a raw UDP message."""
        await self._ensure_transport()
        assert self._transport is not None
        self._transport.sendto(message)

    async def close(self) -> None:
        """Close the underlying transport if open."""
        if self._transport is not None:
            self._transport.close()
            self._transport = None

    async def incr(self, metric: str, value: int = 1) -> None:
        """Increment a counter."""
        self.counters[metric] += value
        msg = f"{self._format(metric)}:{value}|c".encode()
        try:
            await self._send(msg)
        except Exception:
            # Metrics should never crash the app
            pass

    async def gauge(self, metric: str, value: float) -> None:
        """Submit a gauge value."""
        self.gauges[metric] = value
        msg = f"{self._format(metric)}:{value}|g".encode()
        try:
            await self._send(msg)
        except Exception:
            pass

    def reset(self) -> None:
        """Clear stored metrics."""
        self.counters.clear()
        self.gauges.clear()


statsd_client = AsyncStatsDClient(
    settings.statsd.host, settings.statsd.port, settings.statsd.prefix
)

__all__ = ["AsyncStatsDClient", "statsd_client"]
