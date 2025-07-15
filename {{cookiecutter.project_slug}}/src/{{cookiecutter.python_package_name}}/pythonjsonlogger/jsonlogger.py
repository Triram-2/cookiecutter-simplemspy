"""Custom JSON logging formatter for simplified output."""

import json
import logging
from typing import Any, Dict


class JsonFormatter(logging.Formatter):
    """Minimal JSON formatter used for testing."""

    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        log_record: Dict[str, Any] = {
            "name": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(log_record)
