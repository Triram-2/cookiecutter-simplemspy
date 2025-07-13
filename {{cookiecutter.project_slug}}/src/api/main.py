"""Starlette application setup and lifecycle handlers."""

from starlette.applications import Starlette
from starlette.routing import Router

from ..core.logging_config import get_logger
from ..utils import statsd_client, tracer
from . import health, tasks

from .health import router as health_router
from .tasks import router as tasks_router

router = Router()
router.routes.extend(health_router.routes)
router.routes.extend(tasks_router.routes)

log = get_logger(__name__)

app = Starlette(routes=router.routes)


@app.on_event("startup")
async def on_startup() -> None:
    """Log startup message."""

    log.info("Application startup")


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """Clean up resources on shutdown."""

    await _close_repo(health.redis_repo)
    await _close_repo(tasks.tasks_service.repo)
    statsd_client.reset()
    tracer.spans.clear()
    log.info("Application shutdown complete")


async def _close_repo(repo) -> None:
    """Attempt to gracefully close a repository."""

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
