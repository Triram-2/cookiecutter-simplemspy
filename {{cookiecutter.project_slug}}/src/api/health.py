from datetime import datetime, timezone

from starlette.responses import JSONResponse
from starlette.routing import Route, Router

from .. import __version__

router = Router()


async def health_check(request):
    """Return basic service health information."""

    payload = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "redis_connected": True,
        "version": __version__,
    }
    return JSONResponse(payload)

router.routes.append(Route("/health", health_check, methods=["GET"]))
