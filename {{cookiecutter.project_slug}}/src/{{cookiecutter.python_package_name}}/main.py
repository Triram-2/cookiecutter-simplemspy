import asyncio
import uvloop

"""Application entry point.

This module launches the Starlette application via Uvicorn. It can be run
directly with ``python src/{{cookiecutter.python_package_name}}/main.py`` or provided to ``uvicorn`` using the
``{{cookiecutter.python_package_name}}.api:app`` path. Configuration is pulled from
``{{cookiecutter.python_package_name}}.core.config.settings``.
"""

import uvicorn

from {{cookiecutter.python_package_name}}.core.config import settings
from {{cookiecutter.python_package_name}}.core.logging_config import get_logger

log = get_logger(__name__)

if __name__ == "__main__":
    if settings.performance.uvloop_enabled:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    log.info(
        f"Starting {settings.service.name} v{settings.service.version} on "
        f"http://{settings.app_host}:{settings.app_port}"
    )
    log.info(f"Code auto-reloading: {'Enabled' if settings.app_reload else 'Disabled'}")
    log.info("Press CTRL+C to stop the server.")

    uvicorn.run(
        "{{cookiecutter.python_package_name}}.api:app",  # Path to the Starlette application object
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_reload,
    )
