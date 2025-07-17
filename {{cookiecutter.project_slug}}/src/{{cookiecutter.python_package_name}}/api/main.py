"""Starlette application setup and lifecycle handlers."""

from starlette.applications import Starlette
from starlette.routing import Router
from typing import Any

from ..repository.redis_repo import RedisRepository

from ..core.logging_config import get_logger
from ..utils import statsd_client, tracer
from ..middleware import MetricsMiddleware
from ..utils.tracing import shutdown_tracer
from . import health, tasks

from .health import router as health_router
from .tasks import router as tasks_router, start_task_processor, stop_task_processor

router = Router()
router.routes.extend(health_router.routes)
router.routes.extend(tasks_router.routes)

log = get_logger(__name__)

app = Starlette(routes=router.routes)
app.add_middleware(MetricsMiddleware, repo=tasks.tasks_service.repo)


@app.on_event("startup")  # pyright: ignore[reportUnknownMemberType,reportUntypedFunctionDecorator]
async def on_startup() -> None:
    """Log startup message."""
    with tracer.start_as_current_span("запуск"):
        log.info("Application startup")
    await start_task_processor()


@app.on_event("shutdown")  # pyright: ignore[reportUnknownMemberType,reportUntypedFunctionDecorator]
async def on_shutdown() -> None:
    """Clean up resources on shutdown."""
    with tracer.start_as_current_span("остановка"):
        log.info("Application shutdown")
    await _close_repo(health.redis_repo)
    await _close_repo(tasks.tasks_service.repo)
    await stop_task_processor()
    await statsd_client.close()
    statsd_client.reset()
    tracer.spans.clear()
    shutdown_tracer()
    log.info("Application shutdown complete")


async def _close_repo(repo: RedisRepository | Any) -> None:
    """Attempt to gracefully close a repository."""
    with tracer.start_as_current_span("закрытие_репозитория"):
        redis_obj = getattr(repo, "redis", repo)
        close = getattr(redis_obj, "close", None)
        if close:
            try:
                await close()
            except Exception:
                pass
        wait_closed = getattr(redis_obj, "wait_closed", None)
        if wait_closed:
            try:
                await wait_closed()
            except Exception:
                pass
