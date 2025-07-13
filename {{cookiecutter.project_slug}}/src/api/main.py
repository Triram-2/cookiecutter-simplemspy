from starlette.applications import Starlette
from starlette.routing import Router

from .health import router as health_router

router = Router()
router.routes.extend(health_router.routes)

app = Starlette(routes=router.routes)
