from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4

from ..repository.redis_repo import RedisRepository
from ..utils import TASKS_STREAM_NAME


class TasksService:
    """Service handling task enqueueing."""

    def __init__(self, repo: RedisRepository) -> None:
        self.repo = repo

    async def enqueue_task(self, payload: Dict[str, Any]) -> str:
        """Serialize and enqueue a task payload."""
        message = {
            "task_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
            "trace_context": {"trace_id": "", "span_id": ""},
        }
        return await self.repo.add_to_stream(TASKS_STREAM_NAME, message)


__all__ = ["TasksService"]
