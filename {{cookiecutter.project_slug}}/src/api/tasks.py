from __future__ import annotations

from typing import Any, Dict

from pydantic import BaseModel, Field, ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route, Router
from starlette.status import HTTP_202_ACCEPTED, HTTP_400_BAD_REQUEST

from .deps import get_tasks_service
from ..services.tasks_service import TasksService
from ..utils.metrics import statsd_client
from ..utils.tracing import tracer


tasks_service: TasksService = get_tasks_service()


class TaskPayload(BaseModel):
    data: Any
    metadata: Dict[str, Any] = Field(default_factory=dict)


def get_router(service: TasksService | None = None) -> Router:
    service = service or tasks_service
    router = Router()

    async def create_task(request: Request) -> JSONResponse:
        with tracer.start_as_current_span("create_task"):
            try:
                payload = TaskPayload(**await request.json())
            except ValidationError as exc:  # pragma: no cover - Pydantic ensures detail
                return JSONResponse({"detail": exc.errors()}, status_code=HTTP_400_BAD_REQUEST)

            await service.enqueue_task(payload.model_dump())
            await statsd_client.incr("requests.tasks")
            return JSONResponse({"status": "accepted"}, status_code=HTTP_202_ACCEPTED)

    router.routes.append(Route("/tasks", create_task, methods=["POST"]))
    return router


router = get_router()

__all__ = ["router", "get_router", "tasks_service", "TaskPayload"]
