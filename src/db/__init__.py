# src/db/__init__.py
"""
Пакет для взаимодействия с базой данных.

Экспортирует:
- `Base`: Декларативная база SQLAlchemy для определения моделей.
- `TimestampMixin`: Миксин для добавления временных меток created_at и updated_at.
- `get_async_session`: Зависимость FastAPI для получения асинхронной сессии БД.
- `BaseRepository`: Базовый класс для репозиториев с CRUD-операциями.
- `async_engine`: Асинхронный движок SQLAlchemy (если нужен прямой доступ).
"""

from .base import Base, TimestampMixin
from .database import get_async_session, async_engine
from .base_repository import BaseRepository

__all__ = [
    "Base",
    "BaseRepository",
    "TimestampMixin",
    "async_engine",
    "get_async_session",
]
