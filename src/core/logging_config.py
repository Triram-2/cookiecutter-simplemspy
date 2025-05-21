# src/logging_config.py
"""
Модуль для настройки и получения именованных логгеров Loguru.
Предоставляет функцию get_logger, которую можно использовать из любого модуля.
"""
import sys
import logging
import os

from pathlib import Path
from typing import (
    Set,
    Tuple
)
from datetime import datetime

from loguru import logger

from constants import (
    PATH_TO_DIR_LOGS,
    CONSOLE_LOG_FORMAT,
    FILE_LOG_FORMAT,
    DEFAULT_CONSOLE_LEVEL,
    DEFAULT_INFO_FILE_LEVEL,
    DEFAULT_ERROR_FILE_LEVEL,
    DEFAULT_COMPRESSION,
    DEFAULT_ENQUEUE,
    DEFAULT_BACKTRACE,
    DEFAULT_DIAGNOSE
)


_base_logger_configured: bool = False
_configured_file_logger_details: Set[Tuple[str, str]] = set()

class InterceptHandler(logging.Handler):
    """Перехватывает стандартные логи и направляет их в Loguru."""
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        loguru_logger = logger.opt(depth=depth, exception=record.exc_info)
        bound_logger = loguru_logger.bind(name=record.name)
        bound_logger.log(level, record.getMessage())

# --- Приватная функция базовой настройки ---
def _setup_base_loguru_if_needed():
    """Настраивает базовые компоненты (консоль, цвета, перехват), если нужно."""
    global _base_logger_configured
    if _base_logger_configured:
        return

    print("Configuring base Loguru settings (console, intercept)...")
    try:
        logger.remove()

        logger.level("DEBUG", color="<bold><white>")
        logger.level("INFO", color="<bold><green>")
        logger.level("WARNING", color="<bold><yellow>")
        logger.level("ERROR", color="<bold><red>")
        logger.level("CRITICAL", color="<bold><light-red>")

        logger.add(
            sys.stderr,
            format=CONSOLE_LOG_FORMAT,
            level=DEFAULT_CONSOLE_LEVEL.upper(),
            colorize=True,
            enqueue=DEFAULT_ENQUEUE,
            backtrace=DEFAULT_BACKTRACE,
            diagnose=DEFAULT_DIAGNOSE
        )
        print(f"Base console handler added (level: {DEFAULT_CONSOLE_LEVEL.upper()}).")

        logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
        print("Standard logging intercepted by Loguru.")

        _base_logger_configured = True
    except Exception as e:
        print(f"FATAL: Failed to configure base logger: {e}", file=sys.stderr)
        if not _base_logger_configured:
            logger.add(sys.stderr, level="ERROR", colorize=True)
        raise

def get_logger(
    name: str, class_for_get_methods = None,
    # Параметры по умолчанию для файлов
    info_file_level: str = DEFAULT_INFO_FILE_LEVEL,
    error_file_level: str = DEFAULT_ERROR_FILE_LEVEL,
    compression: str | None = DEFAULT_COMPRESSION, # Сжатие все еще полезно
    enqueue: bool = DEFAULT_ENQUEUE,
    backtrace: bool = DEFAULT_BACKTRACE,
    diagnose: bool = DEFAULT_DIAGNOSE
    # rotation и retention убраны, т.к. управляются структурой папок
):
    """
    Получает логгер Loguru для имени `name` со структурой файлов:
    `logs/{info|errors}/{dd_mm}/{name}.log`
    Задаёт методы логирования для класса class_fot_get_methods, если он указан:
    - info(self, message: str)
    - warning(self, message: str)
    - error(self, message: str, exc_info: bool = True)
    - exception(self, message: str)
    - critical(self, message: str, exc_info: bool = True)

    Args:
        name (str): Имя компонента/логгера. Используется для имени файла
                    и фильтрации записей. Не может быть пустым.
        info_file_level (str): Уровень для info-файла.
        error_file_level (str): Уровень для error-файла.
        **kwargs: Другие параметры для `logger.add`, кроме rotation/retention.

    Returns:
        loguru.Logger: Экземпляр логгера с привязанным именем (`logger.bind(name=name)`).
    """
    if not name:
        raise ValueError("Logger name cannot be empty.")

    _setup_base_loguru_if_needed()

    global _configured_file_logger_details
    today_date_str = datetime.now().strftime("%d_%m")
    logger_details = (name, today_date_str)

    if logger_details not in _configured_file_logger_details:
        print(f"Configuring file handlers for logger '{name}' for date '{today_date_str}'...")
        try:
            info_log_dir = Path(PATH_TO_DIR_LOGS) / "info" / today_date_str
            error_log_dir = Path(PATH_TO_DIR_LOGS) / "errors" / today_date_str

            os.makedirs(info_log_dir, exist_ok=True)
            os.makedirs(error_log_dir, exist_ok=True)

            info_log_path = info_log_dir / f"{name}.log"
            error_log_path = error_log_dir / f"{name}.log"

            name_filter = lambda record: record["extra"].get("name") == name

            common_file_args = dict(
                format=FILE_LOG_FORMAT,
                encoding="utf-8",
                enqueue=enqueue,
                backtrace=backtrace,
                diagnose=diagnose,
                filter=name_filter,
                compression=compression,
                rotation=None,
                retention=None
            )

            logger.add(error_log_path, level=error_file_level.upper(), **common_file_args)
            print(f"Added ERROR file handler for '{name}' for date '{today_date_str}': {error_log_path}")

            logger.add(info_log_path, level=info_file_level.upper(), **common_file_args)
            print(f"Added INFO file handler for '{name}' for date '{today_date_str}': {info_log_path}")

            _configured_file_logger_details.add(logger_details)

        except Exception as e:
            print(f"ERROR: Failed to configure file handlers for logger '{name}' for date '{today_date_str}': {e}", file=sys.stderr)

    if class_for_get_methods: # Динамическое присваивание методов лога
        def info(self, message: str):
            self.logger.info(message)

        def warning(self, message: str):
            self.logger.warning(message)

        def error(self, message: str, exc_info: bool = True):
            if exc_info:
                self.logger.opt(exception=True).error(message)
            else:
                self.logger.error(message)

        def exception(self, message: str):
            self.logger.exception(message)

        def critical(self, message: str, exc_info: bool = True):
            if exc_info:
                self.logger.opt(exception=True).critical(message)
            else:
                self.logger.error(message)

        class_for_get_methods.info = info
        class_for_get_methods.warning = warning
        class_for_get_methods.error = error
        class_for_get_methods.exception = exception
        class_for_get_methods.critical = critical

    return logger.bind(name=name)