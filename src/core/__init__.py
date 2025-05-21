# src/core/__init__.py
"""
Основной пакет ядра приложения.

Экспортирует глобальные настройки и утилиту для логирования.
"""

from .config import settings
from .logging_config import get_logger

__all__ = [
    "settings",
    "get_logger",
]

# Можно добавить сюда инициализацию других базовых компонентов ядра,
# если это необходимо при импорте пакета.
# Например, если setup_initial_logger() не вызывается в logging_config.py,
# его можно было бы вызвать здесь, но с осторожностью.
# from .logging_config import setup_initial_logger
# setup_initial_logger() # Потенциально, если убрать авто-вызов из logging_config
