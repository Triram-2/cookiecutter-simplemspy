from datetime import datetime, timezone
from uuid import uuid4
from typing import Any, Dict

from pydantic import BaseModel, Field, ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route, Router
from starlette.status import HTTP_202_ACCEPTED, HTTP_400_BAD_REQUEST

from ..utils import redis_stream, TASKS_STREAM_NAME
from ..utils.metrics import statsd_client
from ..utils.tracing import tracer

router = Router()


class TaskPayload(BaseModel):
    data: Any
    metadata: Dict[str, Any] = Field(default_factory=dict)


async def create_task(request: Request) -> JSONResponse:
    with tracer.start_as_current_span("create_task"):
        try:
            payload = TaskPayload(**await request.json())
        except ValidationError as exc:  # pragma: no cover - Pydantic ensures detail
            return JSONResponse({"detail": exc.errors()}, status_code=HTTP_400_BAD_REQUEST)

        message = {
            "task_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": payload.model_dump(),
            "trace_context": {"trace_id": "", "span_id": ""},
        }
        await redis_stream.xadd(TASKS_STREAM_NAME, message)
        statsd_client.incr("requests.tasks")
        return JSONResponse({"status": "accepted"}, status_code=HTTP_202_ACCEPTED)


router.routes.append(Route("/tasks", create_task, methods=["POST"]))
