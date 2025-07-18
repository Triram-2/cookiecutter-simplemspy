from __future__ import annotations

"""Simple example task processor consuming from Redis Streams."""

import asyncio

# Preserve the original sleep function so tests can monkeypatch ``asyncio.sleep``
# without causing recursive calls. All internal awaits use ``_yield_sleep`` which
# always references the unpatched implementation.
_yield_sleep = asyncio.sleep
import json
from typing import Any, Dict

from ..core.config import settings
from ..utils import DEAD_LETTER_STREAM_NAME, TASKS_STREAM_NAME, tracer

from ..repository.redis_repo import RedisRepository
from ..core.logging_config import get_logger

log = get_logger(__name__)


class TaskProcessor:
    """Consume tasks from Redis and handle them asynchronously."""

    def __init__(self, repo: RedisRepository) -> None:
        self.repo = repo
        self._running = False
        self._task: asyncio.Task[None] | None = None
        self._background_tasks: set[asyncio.Task[Any]] = set()
        self._semaphore = asyncio.Semaphore(settings.performance.max_concurrent_tasks)

    async def start(self) -> None:
        """Start processing tasks in the background."""
        self._running = True
        await self.repo.create_group(TASKS_STREAM_NAME)
        self._task = asyncio.create_task(self._run())
        # ensure the processing loop has a chance to start before returning
        await _yield_sleep(0)

    async def _run(self) -> None:
        while self._running:
            msgs = await self.repo.fetch(TASKS_STREAM_NAME, count=1)
            if not msgs:
                await _yield_sleep(0.1)
                continue
            msg_id, fields = msgs[0]
            task = asyncio.create_task(self._process(msg_id, fields))
            self._background_tasks.add(task)
            task.add_done_callback(self._background_tasks.discard)

    async def handle(self, fields: Dict[str, Any]) -> None:
        """Placeholder task handler."""
        with tracer.start_as_current_span("обработка_задачи"):
            payload = json.loads(fields.get("payload", "{}"))
            log.info("Handled task %s", payload)
            await _yield_sleep(0)

    async def _process(self, msg_id: str, fields: Dict[str, Any]) -> None:
        async with self._semaphore:
            attempts = 0
            while attempts < 3:
                try:
                    await self.handle(fields)
                except Exception as exc:  # pragma: no cover - handler failures
                    attempts += 1
                    log.error(
                        "Task handling failed (attempt %s)", attempts, exc_info=exc
                    )
                    if attempts >= 3:
                        try:
                            await self.repo.add_to_stream(
                                DEAD_LETTER_STREAM_NAME, fields
                            )
                        except (
                            Exception
                        ) as dead_exc:  # pragma: no cover - network errors
                            log.error(
                                "Failed to enqueue to dead-letter", exc_info=dead_exc
                            )
                        break
                    await _yield_sleep(2 ** (attempts - 1))
                else:
                    break
            await self.repo.ack(TASKS_STREAM_NAME, msg_id)

    async def stop(self) -> None:
        """Stop background processing."""
        self._running = False
        if self._task is not None:
            await self._task
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
