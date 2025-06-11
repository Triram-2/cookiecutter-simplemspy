import sys
import os

_src_path = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_src_path)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
# Ensure 'src' is imported and then alias 'name' to 'src' module
# This allows 'from name.module' to effectively become 'from src.module'
import src

sys.modules["name"] = src
"""
Main entry point for running the FastAPI application using Uvicorn.

This file can be used to run the application directly:
  `python src/main.py`

Or passed to Uvicorn for execution:
  `uvicorn name.api:app --reload`
This `main.py` provides a convenient way to launch with settings
from `name.core.config.settings`.
"""

import uvicorn

from name.core.config import settings
from name.core.logging_config import get_logger

log = get_logger(__name__)

if __name__ == "__main__":
    log.info(
        f"Starting Uvicorn server on http://{settings.app_host}:{settings.app_port}"
    )
    log.info(f"Code auto-reloading: {'Enabled' if settings.app_reload else 'Disabled'}")
    log.info("Press CTRL+C to stop the server.")

    uvicorn.run(
        "name.api:app",  # Path to the FastAPI application object
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_reload,
    )
