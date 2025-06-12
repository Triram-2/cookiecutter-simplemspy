"""
Main entry point for running the FastAPI application using Uvicorn.

This file can be used to run the application directly:
  `python src/main.py`

Or passed to Uvicorn for execution:
  `uvicorn src.api:app --reload`  # Changed name.api:app to src.api:app
This `main.py` provides a convenient way to launch with settings
from `src.core.config.settings`. # Changed name.core.config to src.core.config
"""

import uvicorn

from src.core.config import settings # Changed name.core.config to src.core.config
from src.core.logging_config import get_logger # Changed name.core.logging_config to src.core.logging_config

log = get_logger(__name__)

if __name__ == "__main__":
    log.info(
        f"Starting Uvicorn server on http://{settings.app_host}:{settings.app_port}"
    )
    log.info(f"Code auto-reloading: {'Enabled' if settings.app_reload else 'Disabled'}")
    log.info("Press CTRL+C to stop the server.")

    uvicorn.run(
        "src.api:app",  # Path to the FastAPI application object, Changed name.api:app to src.api:app
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_reload,
    )
