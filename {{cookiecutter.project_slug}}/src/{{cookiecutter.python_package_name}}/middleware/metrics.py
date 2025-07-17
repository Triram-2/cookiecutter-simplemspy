"""Middleware for collecting request metrics."""

from __future__ import annotations

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette.requests import Request
from starlette.responses import Response

from ..repository.redis_repo import RedisRepository
from ..utils import TASKS_STREAM_NAME, statsd_client


class MetricsMiddleware(BaseHTTPMiddleware):
    """Measure request duration and queue size via StatsD."""

    def __init__(self, app: ASGIApp, repo: RedisRepository) -> None:
        super().__init__(app)
        self.repo = repo

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[override]
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        await statsd_client.gauge("request_duration", duration_ms)
        try:
            size = await self.repo.length(TASKS_STREAM_NAME)
            await statsd_client.gauge("task_queue_size", float(size))
        except Exception:
            pass
        return response
