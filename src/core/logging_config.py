# src/core/logging_config.py
"""
Модуль для настройки и получения именованных логгеров Loguru.
Использует конфигурацию из src.core.config.settings.
"""

import sys
import logging
import os
from datetime import datetime

from loguru import logger
from .config import settings  # Импортируем наши Pydantic настройки


# --- Перехватчик стандартного логирования ---
class InterceptHandler(logging.Handler):
    """
    Перехватывает стандартные сообщения логирования Python
    и направляет их в Loguru.
    """

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).bind(name=record.name).log(
            level, record.getMessage()
        )


# --- Базовая настройка логгера при импорте модуля ---
def setup_initial_logger():
    """
    Настраивает базовый логгер Loguru (консольный вывод и перехват).
    Эта функция должна вызываться один раз при старте приложения.
    """
    logger.remove()  # Удаляем все предыдущие обработчики, чтобы избежать дублирования

    # Настройка уровней и их цветов (можно вынести в config, если нужна гибкость)
    logger.level("DEBUG", color="<bold><white>")
    logger.level("INFO", color="<bold><green>")
    logger.level("WARNING", color="<bold><yellow>")
    logger.level("ERROR", color="<bold><red>")
    logger.level("CRITICAL", color="<bold><light-red>")

    # Добавляем консольный обработчик из настроек
    logger.add(
        sys.stderr,
        format=settings.log.console_format,
        level=settings.log.console_level.upper(),
        colorize=True,
        enqueue=settings.log.enqueue,
        backtrace=settings.log.backtrace,
        diagnose=settings.log.diagnose,
    )

    # Перехватываем стандартное логирование Python
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    logger.info(
        "Базовый логгер Loguru сконфигурирован (консоль, перехват стандартных логов)."
    )


# Выполняем базовую настройку при импорте модуля
setup_initial_logger()


# --- Функция для получения настроенного логгера ---
def get_logger(name: str):
    """
    Получает и настраивает логгер Loguru для указанного имени.

    Для каждого имени (`name`) будут настроены файловые обработчики
    (для info и error уровней), пишущие в отдельные файлы.

    Args:
        name (str): Имя компонента/модуля для логгера.
                    Используется для тега в логах и имени файла.

    Returns:
        loguru.Logger: Экземпляр логгера, привязанный к указанному имени.
    """
    if not name:
        bound_logger = logger.bind(name="unnamed_logger")
        logger.error(
            "Имя логгера не может быть пустым! Попытка получить логгер без имени."
        )
        return bound_logger

    today_date_str = datetime.now().strftime("%d_%m")

    # Проверка прав на базовую директорию логов
    if not os.path.exists(settings.log.path):
        logger.error(f"Базовая директория для логов не найдена: {settings.log.path}")
        try:
            os.makedirs(settings.log.path, exist_ok=True)
            if not os.access(settings.log.path, os.W_OK):
                logger.error(
                    f"Нет прав на запись в базовую директорию логов (после создания): {settings.log.path}"
                )
                return logger.bind(name=name)
        except Exception as e:
            logger.error(
                f"Ошибка при создании базовой директории логов {settings.log.path}: {e}"
            )
            return logger.bind(name=name)
    elif not os.access(settings.log.path, os.W_OK):
        logger.error(
            f"Нет прав на запись в базовую директорию логов: {settings.log.path}"
        )
        return logger.bind(name=name)

    info_log_dir = settings.log.path / "info" / today_date_str
    error_log_dir = settings.log.path / "errors" / today_date_str

    try:
        os.makedirs(info_log_dir, exist_ok=True)
        if not os.access(info_log_dir, os.W_OK):
            logger.error(f"Нет прав на запись в директорию info логов: {info_log_dir}")
    except Exception as e:
        logger.error(f"Ошибка при создании директории info логов {info_log_dir}: {e}")

    try:
        os.makedirs(error_log_dir, exist_ok=True)
        if not os.access(error_log_dir, os.W_OK):
            logger.error(
                f"Нет прав на запись в директорию error логов: {error_log_dir}"
            )
    except Exception as e:
        logger.error(f"Ошибка при создании директории error логов {error_log_dir}: {e}")

    info_log_path = info_log_dir / f"{name}.log"
    error_log_path = error_log_dir / f"{name}.log"

    name_filter = lambda record: record["extra"].get("name") == name

    # Аргументы для файловых обработчиков, когда Loguru управляет файлом по пути
    base_file_args = {
        "format": settings.log.file_format,
        "encoding": "utf-8",
        "enqueue": settings.log.enqueue,
        "backtrace": settings.log.backtrace,
        "diagnose": settings.log.diagnose,
        "compression": settings.log.compression,
        "rotation": settings.log.rotation,
        "retention": settings.log.retention,
        "catch": True,
    }

    # Настройка error-лога (используем путь к файлу)
    error_log_args = base_file_args.copy()
    error_log_args["filter"] = name_filter
    try:
        logger.add(
            error_log_path,  # Используем путь к файлу
            level=settings.log.error_file_level.upper(),
            **error_log_args,
        )
    except Exception as e:
        print(
            f"КРИТИЧЕСКАЯ ОШИБКА: Не удалось настроить error-лог для {name} по пути {error_log_path}: {e}",
            file=sys.stderr,
        )

    # Настройка info-лога (используем путь к файлу)
    def info_filter_func(record):
        if record["extra"].get("name") != name:
            return False
        is_at_least_info_level = (
            record["level"].no >= logger.level(settings.log.info_file_level.upper()).no
        )
        is_below_error_level = (
            record["level"].no < logger.level(settings.log.error_file_level.upper()).no
        )
        return is_at_least_info_level and is_below_error_level

    info_log_args = base_file_args.copy()
    # info_log_args.pop('filter', None) # Не нужно, т.к. filter не в base_file_args
    # и мы добавляем новый 'filter' ключ ниже
    info_log_args["filter"] = info_filter_func

    try:
        logger.add(
            info_log_path,  # Используем путь к файлу
            level=settings.log.info_file_level.upper(),
            **info_log_args,
        )
    except Exception as e:
        print(
            f"КРИТИЧЕСКАЯ ОШИБКА: Не удалось настроить info-лог для {name} по пути {info_log_path}: {e}",
            file=sys.stderr,
        )

    return logger.bind(name=name)
