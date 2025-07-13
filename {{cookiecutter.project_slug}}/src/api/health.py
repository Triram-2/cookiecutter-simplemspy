from starlette.responses import JSONResponse
from starlette.routing import Route, Router

router = Router()


async def health_check(request):
    return JSONResponse({"status": "healthy"})

router.routes.append(Route("/health", health_check, methods=["GET"]))
