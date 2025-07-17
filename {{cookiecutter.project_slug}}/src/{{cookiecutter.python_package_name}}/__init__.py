"""Root package of the application."""

from .core.config import settings
from .core.logging_config import get_logger

__all__ = ["__version__", "get_logger", "settings"]

log = get_logger(__name__)

__version__: str = "{{cookiecutter.project_version}}"
