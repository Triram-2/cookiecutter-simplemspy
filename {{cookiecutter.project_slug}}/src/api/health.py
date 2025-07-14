from __future__ import annotations

"""Health check endpoint definitions."""

from datetime import datetime, timezone
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route, Router
from starlette.status import HTTP_200_OK, HTTP_503_SERVICE_UNAVAILABLE

from .deps import get_redis_repo
from ..utils.metrics import statsd_client
from ..utils.tracing import tracer
from ..repository.redis_repo import RedisRepository
from .. import __version__


redis_repo: RedisRepository = get_redis_repo()


def get_router(repo: RedisRepository | None = None) -> Router:
    """
    Create router with health endpoint.

    Args:
        repo: Custom repository instance. Defaults to global ``redis_repo``.

    Returns:
        Router with the ``/health`` route attached.
    """
    repo = repo or redis_repo
    router = Router()

    async def health_check(request: Request) -> JSONResponse:
        """
        Return basic service health information.

        Args:
            request: Incoming HTTP request.

        Returns:
            JSONResponse with health metadata.
        """
        with tracer.start_as_current_span("health_check"):
            await statsd_client.incr("requests.health")
            try:
                await repo.ping()
                redis_ok = True
            except Exception:  # pragma: no cover - redis ping failures
                redis_ok = False

            payload = {
                "status": "healthy" if redis_ok else "unhealthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "redis_connected": redis_ok,
                "version": __version__,
            }
            status_code = HTTP_200_OK if redis_ok else HTTP_503_SERVICE_UNAVAILABLE
            return JSONResponse(payload, status_code=status_code)

    router.routes.append(Route("/health", health_check, methods=["GET"]))
    return router


router = get_router()

__all__ = ["get_router", "redis_repo", "router"]
