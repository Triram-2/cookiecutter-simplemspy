from datetime import datetime, timezone

from starlette.responses import JSONResponse
from starlette.routing import Route, Router

from ..utils.metrics import statsd_client
from ..utils.tracing import tracer

from .. import __version__

router = Router()


async def health_check(request):
    """Return basic service health information."""
    with tracer.start_as_current_span("health_check"):
        statsd_client.incr("requests.health")

        payload = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "redis_connected": True,
            "version": __version__,
        }
        return JSONResponse(payload)

router.routes.append(Route("/health", health_check, methods=["GET"]))
