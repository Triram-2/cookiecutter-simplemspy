"""Logging configuration helpers using ``loguru``."""

import sys
import logging
import os
import json
from datetime import datetime
from pathlib import Path
from types import FrameType
from typing import Any, Callable, Dict, Union, TextIO, cast

from loguru import logger as loguru_logger
import httpx

_logger_initialized = False

from .config import settings, AppSettings


loguru_logger.disable("httpx")
logging.getLogger("httpx").handlers = [logging.NullHandler()]
logging.getLogger("httpx").propagate = False


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        level: Union[str, int]
        try:
            level = loguru_logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame: FrameType | None = cast(FrameType | None, logging.currentframe())
        depth: int = 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        loguru_logger.opt(depth=depth, exception=record.exc_info).bind(
            name=record.name
        ).log(level, record.getMessage())


def setup_initial_logger() -> None:
    loguru_logger.remove()

    loguru_logger.level("DEBUG", color="<bold><white>")
    loguru_logger.level("INFO", color="<bold><green>")
    loguru_logger.level("WARNING", color="<bold><yellow>")
    loguru_logger.level("ERROR", color="<bold><red>")
    loguru_logger.level("CRITICAL", color="<bold><light-red>")

    current_settings: AppSettings = settings

    loguru_logger.add(
        cast(TextIO, sys.stderr),
        serialize=True,
        level=current_settings.log.console_level.upper(),
        enqueue=current_settings.log.enqueue,
        backtrace=current_settings.log.backtrace,
        diagnose=current_settings.log.diagnose,
    )

    def _send_to_loki(message: Any) -> None:
        """Forward log records to a Grafana Loki instance."""
        record = message.record
        formatted = json.dumps(
            {
                "message": record.get("message", ""),
                "level": record["level"].name,
                "logger": record["extra"].get("name", ""),
            }
        )
        timestamp = int(record["time"].timestamp() * 1_000_000_000)
        payload = {
            "streams": [
                {
                    "stream": {"app": current_settings.service.name},
                    "values": [[str(timestamp), formatted]],
                }
            ]
        }
        try:
            httpx.post(current_settings.log.loki_endpoint, json=payload, timeout=5)
        except Exception as exc:  # pragma: no cover - network errors
            print(f"Loki logging failed: {exc}", file=sys.stderr)

    if current_settings.log.loki_endpoint:
        loguru_logger.add(
            _send_to_loki, level=current_settings.log.console_level.upper()
        )

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    globals()["_logger_initialized"] = True

    def _patch_uvicorn_loggers() -> None:
        """
        Заставить uvicorn.* логгеры ходить через root,
        где уже стоит InterceptHandler.
        """
        for name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
            logger = logging.getLogger(name)
            logger.handlers = []
            logger.propagate = True

    _patch_uvicorn_loggers()


__all__ = ["InterceptHandler", "get_logger", "setup_initial_logger"]


def get_logger(name: str) -> Any:
    if not _logger_initialized:
        setup_initial_logger()

    if not name:
        return loguru_logger.bind(name="unnamed_logger_error")

    current_settings: AppSettings = settings
    log_path_base: Path = current_settings.log.path
    today_date_str: str = datetime.now().strftime("%d_%m")

    if not log_path_base.exists():
        try:
            os.makedirs(log_path_base, exist_ok=True)
            if not os.access(log_path_base, os.W_OK):
                return loguru_logger.bind(name=name)
        except Exception:
            return loguru_logger.bind(name=name)
    elif not os.access(log_path_base, os.W_OK):
        return loguru_logger.bind(name=name)

    info_log_dir: Path = log_path_base / "info" / today_date_str
    error_log_dir: Path = log_path_base / "errors" / today_date_str

    def _ensure_log_dir_writable(log_dir: Path) -> bool:
        try:
            os.makedirs(log_dir, exist_ok=True)
            if not os.access(log_dir, os.W_OK):
                return False
            return True
        except Exception:
            return False

    if not _ensure_log_dir_writable(info_log_dir) or not _ensure_log_dir_writable(
        error_log_dir
    ):
        return loguru_logger.bind(name=name)

    info_log_path: Path = info_log_dir / f"{name}.log"
    error_log_path: Path = error_log_dir / f"{name}.log"

    name_filter: Callable[[Dict[str, Any]], bool] = (
        lambda record: record["extra"].get("name") == name
    )

    base_file_args: Dict[str, Any] = {
        "format": current_settings.log.file_format,
        "encoding": "utf-8",
        "enqueue": current_settings.log.enqueue,
        "backtrace": current_settings.log.backtrace,
        "diagnose": current_settings.log.diagnose,
        "compression": current_settings.log.compression,
        "rotation": current_settings.log.rotation,
        "retention": current_settings.log.retention,
        "catch": True,
    }

    error_log_args: Dict[str, Any] = base_file_args.copy()
    error_log_args["filter"] = name_filter
    try:
        loguru_logger.add(
            error_log_path,
            level=current_settings.log.error_file_level.upper(),
            **error_log_args,
        )
    except Exception:
        pass

    def info_filter_func(record: Dict[str, Any]) -> bool:
        if record["extra"].get("name") != name:
            return False
        current_record_level_no: int = record["level"].no
        info_config_level_no: int = loguru_logger.level(
            current_settings.log.info_file_level.upper()
        ).no
        error_config_level_no: int = loguru_logger.level(
            current_settings.log.error_file_level.upper()
        ).no
        is_at_least_info_level: bool = current_record_level_no >= info_config_level_no
        is_below_error_level: bool = current_record_level_no < error_config_level_no
        return is_at_least_info_level and is_below_error_level

    info_log_args: Dict[str, Any] = base_file_args.copy()
    info_log_args["filter"] = info_filter_func

    try:
        loguru_logger.add(
            info_log_path,
            level=current_settings.log.info_file_level.upper(),
            **info_log_args,
        )
    except Exception:
        pass

    return loguru_logger.bind(name=name)
