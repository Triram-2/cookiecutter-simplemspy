from __future__ import annotations

"""Simple example task processor consuming from Redis Streams."""

import asyncio
import json
from typing import Any, Dict

from ..repository.redis_repo import RedisRepository
from ..core.logging_config import get_logger
from ..utils import TASKS_STREAM_NAME, tracer

log = get_logger(__name__)


class TaskProcessor:
    """Consume tasks from Redis and handle them asynchronously."""

    def __init__(self, repo: RedisRepository) -> None:
        self.repo = repo
        self._running = False
        self._task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        """Start processing tasks in the background."""
        self._running = True
        await self.repo.create_group(TASKS_STREAM_NAME)
        tracer.spans.clear()
        self._task = asyncio.create_task(self._run())

    async def _run(self) -> None:
        while self._running:
            msgs = await self.repo.fetch(TASKS_STREAM_NAME, count=1)
            if not msgs:
                await asyncio.sleep(0.1)
                continue
            msg_id, fields = msgs[0]
            await self.handle(fields)
            await self.repo.ack(TASKS_STREAM_NAME, msg_id)

    async def handle(self, fields: Dict[str, Any]) -> None:
        """Placeholder task handler."""
        with tracer.start_as_current_span("обработка_задачи"):
            payload = json.loads(fields.get("payload", "{}"))
            log.info("Handled task %s", payload)
            await asyncio.sleep(0)

    async def stop(self) -> None:
        """Stop background processing."""
        self._running = False
        if self._task is not None:
            await self._task
