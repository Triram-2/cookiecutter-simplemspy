"""Root package of the application."""

from .core.config import settings
from .core.logging_config import get_logger

__all__ = ["__version__", "settings", "get_logger"]

log = get_logger(__name__)

# Version of the generated service.  This constant is used in runtime
# checks, e.g. the health endpoint.
__version__: str = "0.1.0"
