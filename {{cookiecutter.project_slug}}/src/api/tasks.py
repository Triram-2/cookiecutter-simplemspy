from __future__ import annotations

"""Task creation endpoint definitions."""

import json
from html import escape
from typing import Any, Dict

import asyncio
from pydantic import BaseModel, Field, ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route, Router
from starlette.status import (
    HTTP_202_ACCEPTED,
    HTTP_400_BAD_REQUEST,
    HTTP_413_REQUEST_ENTITY_TOO_LARGE,
)

from .deps import get_tasks_service
from ..services.tasks_service import TasksService
from ..utils.metrics import statsd_client
from ..utils.tracing import tracer
from ..core.config import settings


tasks_service: TasksService = get_tasks_service()

# Keep references to background tasks to prevent premature garbage collection.
background_tasks: set[asyncio.Task[Any]] = set()


MAX_BODY_SIZE = settings.performance.max_payload_size


def _sanitize(value: Any) -> Any:
    """
    Escape potentially unsafe strings in payloads.

    Args:
        value: Arbitrary value to sanitize.

    Returns:
        The sanitized value.
    """
    if isinstance(value, str):
        return escape(value)
    if isinstance(value, list):
        return [_sanitize(v) for v in value]
    if isinstance(value, dict):
        return {k: _sanitize(v) for k, v in value.items()}
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
        Router with the ``/tasks`` route registered.
    """
    service = service or tasks_service
    router = Router()

    async def create_task(request: Request) -> JSONResponse:
        """
        Validate payload and enqueue task asynchronously.

        Args:
            request: Incoming HTTP request.

        Returns:
            JSONResponse indicating acceptance or validation error.
        """
        with tracer.start_as_current_span("create_task"):
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

            task_metric = asyncio.create_task(
                statsd_client.incr("requests.tasks")
            )
            background_tasks.add(task_metric)
            task_metric.add_done_callback(background_tasks.discard)
            return JSONResponse({"status": "accepted"}, status_code=HTTP_202_ACCEPTED)

    router.routes.append(Route("/tasks", create_task, methods=["POST"]))
    return router


router = get_router()

__all__ = ["TaskPayload", "get_router", "router", "tasks_service"]
