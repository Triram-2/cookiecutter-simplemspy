from datetime import datetime, timezone

from starlette.responses import JSONResponse
from starlette.routing import Route, Router
from starlette.status import HTTP_200_OK, HTTP_503_SERVICE_UNAVAILABLE

from ..utils.metrics import statsd_client
from ..utils.tracing import tracer
from ..utils import redis_stream

from .. import __version__

router = Router()


async def health_check(request):
    """Return basic service health information."""
    with tracer.start_as_current_span("health_check"):
        await statsd_client.incr("requests.health")

        try:
            await redis_stream.ping()
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
