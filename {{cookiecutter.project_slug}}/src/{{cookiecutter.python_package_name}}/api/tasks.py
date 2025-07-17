from __future__ import annotations

"""Task creation endpoint definitions."""

import json
from html import escape
from typing import Any, Dict, Mapping, Sequence, cast

import asyncio
from pydantic import BaseModel, Field, ValidationError  # pyright: ignore[reportMissingImports]
from starlette.requests import Request  # pyright: ignore[reportMissingImports]
from starlette.responses import JSONResponse  # pyright: ignore[reportMissingImports]
from starlette.routing import Route, Router  # pyright: ignore[reportMissingImports]
from starlette.status import (
    HTTP_202_ACCEPTED,
    HTTP_400_BAD_REQUEST,
    HTTP_413_REQUEST_ENTITY_TOO_LARGE,
)

from .deps import get_tasks_service
from ..services.tasks_service import TasksService
from ..services.task_processor import TaskProcessor
from ..utils.metrics import statsd_client
from ..utils.tracing import tracer
from ..utils import TASKS_ENDPOINT_PATH
from ..core.config import settings
from ..core.logging_config import get_logger

log = get_logger(__name__)


tasks_service: TasksService = get_tasks_service()
task_processor: TaskProcessor | None = None

background_tasks: set[asyncio.Task[Any]] = set()


def _log_task_result(task: asyncio.Task[Any]) -> None:
    try:
        task.result()
    except Exception as exc:  # pragma: no cover - background task errors
        log.error("Background task failed", exc_info=exc)


MAX_BODY_SIZE = settings.performance.max_payload_size


async def start_task_processor() -> None:
    """Start background task processor."""
    global task_processor
    if task_processor is None:
        task_processor = TaskProcessor(tasks_service.repo)
    await task_processor.start()


async def stop_task_processor() -> None:
    """Stop background task processor."""
    global task_processor
    if task_processor is not None:
        await task_processor.stop()
        task_processor = None


def _sanitize(value: Any) -> Any:
    """
    Escape potentially unsafe strings in payloads.

    Args:
        value: Arbitrary value to sanitize.

    Returns:
        The sanitized value.
    """
    with tracer.start_as_current_span("очистка"):
        if isinstance(value, str):
            return escape(value)
        if isinstance(value, Sequence) and not isinstance(
            value, str | bytes | bytearray
        ):
            seq = cast(Sequence[Any], value)
            return [_sanitize(v) for v in seq]
        if isinstance(value, Mapping):
            mapping = cast(Mapping[Any, Any], value)
            return {str(k): _sanitize(v) for k, v in mapping.items()}
        return value


class TaskPayload(BaseModel):
    """Payload for a single task request."""

    data: Any
    metadata: Dict[str, Any] = Field(default_factory=dict)


def get_router(service: TasksService | None = None) -> Router:
    """
    Create router for task creation endpoint.

    Args:
        service: Service instance used to enqueue tasks. Defaults to
            the global ``tasks_service``.

    Returns:
        Router with the ``TASKS_ENDPOINT_PATH`` route registered.
    """
    service = service or tasks_service
    with tracer.start_as_current_span("получение_роутера"):
        router = Router()

    async def create_task(request: Request) -> JSONResponse:
        """
        Validate payload and enqueue task asynchronously.

        Args:
            request: Incoming HTTP request.

        Returns:
            JSONResponse indicating acceptance or validation error.
        """
        with tracer.start_as_current_span("создание_задачи"):
            body = await request.body()
            if len(body) > MAX_BODY_SIZE:
                return JSONResponse(
                    {"detail": "Payload too large"},
                    status_code=HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                )
            try:
                raw = json.loads(body.decode())
                sanitized = _sanitize(raw)
                payload = TaskPayload(**sanitized)
            except json.JSONDecodeError:
                return JSONResponse(
                    {"detail": "Invalid JSON"}, status_code=HTTP_400_BAD_REQUEST
                )
            except ValidationError as exc:  # pragma: no cover - Pydantic ensures detail
                return JSONResponse(
                    {"detail": exc.errors()}, status_code=HTTP_400_BAD_REQUEST
                )

            task_enqueue = asyncio.create_task(
                service.enqueue_task(payload.model_dump())
            )
            background_tasks.add(task_enqueue)
            task_enqueue.add_done_callback(background_tasks.discard)
            task_enqueue.add_done_callback(_log_task_result)

            task_metric = asyncio.create_task(statsd_client.incr("requests.tasks"))
            background_tasks.add(task_metric)
            task_metric.add_done_callback(background_tasks.discard)
            task_metric.add_done_callback(_log_task_result)
            return JSONResponse({"status": "accepted"}, status_code=HTTP_202_ACCEPTED)

    router.routes.append(Route(TASKS_ENDPOINT_PATH, create_task, methods=["POST"]))
    return router


router = get_router()

__all__ = [
    "TaskPayload",
    "get_router",
    "router",
    "tasks_service",
    "task_processor",
    "start_task_processor",
    "stop_task_processor",
]
