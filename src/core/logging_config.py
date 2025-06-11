# src/core/logging_config.py
"""
Модуль для настройки и получения именованных логгеров Loguru.
Использует конфигурацию из src.core.config.settings.
"""

import sys
import logging
import os
from datetime import datetime
from pathlib import Path
from types import FrameType  # For typing frame objects
from typing import Any, Callable, Dict, Optional, Union, TextIO, cast

from loguru import logger as loguru_logger

# Removed: from loguru._logger import Logger as LoguruLoggerType
from .config import settings, AppSettings  # Import AppSettings for typing 'settings'


# Removed _LoggerType TypeAlias and its TYPE_CHECKING block


# --- Перехватчик стандартного логирования ---
class InterceptHandler(logging.Handler):
    """
    Перехватывает стандартные сообщения логирования Python
    и направляет их в Loguru.
    """

    def emit(self, record: logging.LogRecord) -> None:
        level: Union[str, int]
        try:
            level = loguru_logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame: Optional[FrameType] = cast(Optional[FrameType], logging.currentframe())
        depth: int = 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore # frame can be None here
            depth += 1

        # Ensure frame is not None before accessing f_code, though opt should handle it
        # The use of .bind(name=record.name) is good.
        loguru_logger.opt(depth=depth, exception=record.exc_info).bind(
            name=record.name
        ).log(level, record.getMessage())


# --- Базовая настройка логгера при импорте модуля ---
def setup_initial_logger() -> None:
    """
    Настраивает базовый логгер Loguru (консольный вывод и перехват).
    Эта функция должна вызываться один раз при старте приложения.
    """
    loguru_logger.remove()  # Удаляем все предыдущие обработчики

    # Настройка уровней и их цветов
    loguru_logger.level("DEBUG", color="<bold><white>")
    loguru_logger.level("INFO", color="<bold><green>")
    loguru_logger.level("WARNING", color="<bold><yellow>")
    loguru_logger.level("ERROR", color="<bold><red>")
    loguru_logger.level("CRITICAL", color="<bold><light-red>")

    # Используем AppSettings для типизации settings
    current_settings: AppSettings = settings

    # Добавляем консольный обработчик из настроек
    # sys.stderr is TextIO
    loguru_logger.add(
        cast(TextIO, sys.stderr),  # Sink can be TextIO
        format=current_settings.log.console_format,
        level=current_settings.log.console_level.upper(),
        colorize=True,  # bool
        enqueue=current_settings.log.enqueue,  # bool
        backtrace=current_settings.log.backtrace,  # bool
        diagnose=current_settings.log.diagnose,  # bool
    )

    # Перехватываем стандартное логирование Python
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    loguru_logger.info(
        "Базовый логгер Loguru сконфигурирован (консоль, перехват стандартных логов)."
    )


# Выполняем базовую настройку при импорте модуля
setup_initial_logger()


# --- Функция для получения настроенного логгера ---
# Change return type to loguru.Logger (public type)
def get_logger(name: str) -> Any:
    """
    Получает и настраивает логгер Loguru для указанного имени.
    Файловые обработчики (info, error) настраиваются для каждого имени.
    """
    if not name:  # Ensure name is not empty
        # Log an error and return a default bound logger
        loguru_logger.error(
            "Имя логгера не может быть пустым! Попытка получить логгер без имени."
        )
        return loguru_logger.bind(name="unnamed_logger_error")

    current_settings: AppSettings = settings
    log_path_base: Path = current_settings.log.path
    today_date_str: str = datetime.now().strftime("%d_%m")

    # Проверка прав на базовую директорию логов
    if not log_path_base.exists():
        loguru_logger.error(f"Базовая директория для логов не найдена: {log_path_base}")
        try:
            os.makedirs(log_path_base, exist_ok=True)
            if not os.access(log_path_base, os.W_OK):
                loguru_logger.error(
                    f"Нет прав на запись в базовую директорию логов (после создания): {log_path_base}"
                )
                return loguru_logger.bind(name=name)  # Return before further setup
        except Exception as e:
            loguru_logger.error(
                f"Ошибка при создании базовой директории логов {log_path_base}: {e}"
            )
            return loguru_logger.bind(name=name)
    elif not os.access(log_path_base, os.W_OK):
        loguru_logger.error(
            f"Нет прав на запись в базовую директорию логов: {log_path_base}"
        )
        return loguru_logger.bind(name=name)

    info_log_dir: Path = log_path_base / "info" / today_date_str
    error_log_dir: Path = log_path_base / "errors" / today_date_str

    # Helper to create dirs and check access, reducing repetition
    def _ensure_log_dir_writable(log_dir: Path) -> bool:
        try:
            os.makedirs(log_dir, exist_ok=True)
            if not os.access(log_dir, os.W_OK):
                loguru_logger.error(f"Нет прав на запись в директорию логов: {log_dir}")
                return False
            return True
        except Exception as e:
            loguru_logger.error(
                f"Ошибка при создании/проверке директории логов {log_dir}: {e}"
            )
            return False

    if not _ensure_log_dir_writable(info_log_dir) or not _ensure_log_dir_writable(
        error_log_dir
    ):
        # If directories cannot be prepared, return a logger bound to the name but without file handlers
        return loguru_logger.bind(name=name)

    info_log_path: Path = info_log_dir / f"{name}.log"
    error_log_path: Path = error_log_dir / f"{name}.log"

    # Filter type: Callable[[Dict[str, Any]], bool]
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
        "rotation": current_settings.log.rotation,  # str
        "retention": current_settings.log.retention,  # str
        "catch": True,  # bool
    }

    # Настройка error-лога
    error_log_args: Dict[str, Any] = base_file_args.copy()
    error_log_args["filter"] = name_filter
    try:
        loguru_logger.add(
            error_log_path,  # Sink can be Path
            level=current_settings.log.error_file_level.upper(),  # str
            **error_log_args,
        )
    except Exception as e:
        # Using sys.stderr for critical bootstrap errors
        print(
            f"КРИТИЧЕСКАЯ ОШИБКА: Не удалось настроить error-лог для {name} по пути {error_log_path}: {e}",
            file=sys.stderr,
        )

    # Настройка info-лога
    # Filter type: Callable[[Dict[str, Any]], bool]
    def info_filter_func(record: Dict[str, Any]) -> bool:
        if record["extra"].get("name") != name:
            return False

        # Accessing level object and its 'no' attribute
        # record["level"] is a loguru._logger.Level Object
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
            info_log_path,  # Sink can be Path
            level=current_settings.log.info_file_level.upper(),  # str
            **info_log_args,
        )
    except Exception as e:
        print(
            f"КРИТИЧЕСКАЯ ОШИБКА: Не удалось настроить info-лог для {name} по пути {info_log_path}: {e}",
            file=sys.stderr,
        )

    return loguru_logger.bind(name=name)
