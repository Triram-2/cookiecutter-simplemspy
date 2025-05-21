# src/core/logging_config.py
"""
Модуль для настройки и получения именованных логгеров Loguru.
Использует конфигурацию из src.core.config.settings.
"""
import sys
import logging
import os
from pathlib import Path
from datetime import datetime

from loguru import logger
from .config import settings # Импортируем наши Pydantic настройки

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
        
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, 
            record.getMessage()
        )

# --- Базовая настройка логгера при импорте модуля ---
def setup_initial_logger():
    """
    Настраивает базовый логгер Loguru (консольный вывод и перехват).
    Эта функция должна вызываться один раз при старте приложения.
    """
    logger.remove() # Удаляем все предыдущие обработчики, чтобы избежать дублирования

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
        diagnose=settings.log.diagnose
    )
    
    # Перехватываем стандартное логирование Python
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    logger.info("Базовый логгер Loguru сконфигурирован (консоль, перехват стандартных логов).")

# Выполняем базовую настройку при импорте модуля
# Этот вызов может приводить к проблемам, если модуль импортируется несколько раз
# в разных местах до полной инициализации приложения.
# Рекомендуется вызывать setup_initial_logger() явно при старте приложения.
# Пока оставим так для простоты, но это место для возможного улучшения.
setup_initial_logger()


# --- Функция для получения настроенного логгера ---
def get_logger(name: str):
    """
    Получает и настраивает логгер Loguru для указанного имени.

    Для каждого имени (`name`) будут настроены файловые обработчики 
    (для info и error уровней), пишущие в отдельные файлы.
    Структура лог-файлов: {settings.log.path}/{info|errors}/{dd_mm}/{name}.log

    Args:
        name (str): Имя компонента/модуля для логгера. 
                    Используется для тега в логах и имени файла.

    Returns:
        loguru.Logger: Экземпляр логгера, привязанный к указанному имени.
    """
    if not name:
        # Это не должно происходить, если используется корректно, но для безопасности
        bound_logger = logger.bind(name="unnamed_logger")
        bound_logger.error("Имя логгера не может быть пустым!")
        return bound_logger

    # Определяем пути для лог-файлов на основе текущей даты и имени
    today_date_str = datetime.now().strftime("%d_%m")
    
    info_log_dir = settings.log.path / "info" / today_date_str
    error_log_dir = settings.log.path / "errors" / today_date_str

    os.makedirs(info_log_dir, exist_ok=True)
    os.makedirs(error_log_dir, exist_ok=True)

    info_log_path = info_log_dir / f"{name}.log"
    error_log_path = error_log_dir / f"{name}.log"

    # Фильтр для записей конкретного логгера (по имени)
    name_filter = lambda record: record["extra"].get("name") == name

    # Общие аргументы для файловых обработчиков
    common_file_args = dict(
        format=settings.log.file_format,
        encoding="utf-8",
        enqueue=settings.log.enqueue,
        backtrace=settings.log.backtrace,
        diagnose=settings.log.diagnose,
        filter=name_filter, 
        compression=settings.log.compression,
        rotation=settings.log.rotation, 
        retention=settings.log.retention,
    )

    # Формируем уникальные идентификаторы для обработчиков, чтобы избежать их повторного добавления
    # Loguru >= 0.6.0 должен сам справляться с этим лучше, но для надежности можно использовать sink id.
    # Однако, явное указание sink id может быть сложным, если мы хотим разные файлы для разных 'name'.
    # Вместо этого, мы полагаемся на то, что logger.add идемпотентен для одинаковых параметров.
    # Но для разных 'name' нам НУЖНО добавлять новые обработчики.
    # Проблема может быть, если get_logger вызывается многократно с ОДНИМ И ТЕМ ЖЕ именем в рамках одного запуска.
    # Loguru должен корректно обрабатывать это, не добавляя дублирующие обработчики с идентичными параметрами.

    # Добавляем обработчик для error-логов
    logger.add(
        error_log_path, 
        level=settings.log.error_file_level.upper(), 
        **common_file_args
    )
    
    # Добавляем обработчик для info-логов
    # Дополнительный фильтр, чтобы error+ логи не дублировались, если info_level ниже error_level
    # и также чтобы info логи не попадали в error файл (хотя уровень это уже должен регулировать)
    def info_filter(record):
        is_correct_name = name_filter(record)
        is_below_error_level = record["level"].no < logger.level(settings.log.error_file_level.upper()).no
        return is_correct_name and is_below_error_level

    logger.add(
        info_log_path, 
        level=settings.log.info_file_level.upper(),
        filter=info_filter, # Используем комбинированный фильтр
        **common_file_args
    )
    
    return logger.bind(name=name)
