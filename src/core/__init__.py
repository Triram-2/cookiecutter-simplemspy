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
