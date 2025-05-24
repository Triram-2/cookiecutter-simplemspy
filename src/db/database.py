# src/db/database.py
"""
Модуль для настройки подключения к базе данных с использованием SQLAlchemy.
Предоставляет асинхронный движок (engine) и фабрику сессий.
"""

from typing import AsyncGenerator, Generator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import (
    sessionmaker,
)  # Для возможного использования синхронных частей, если потребуется
from sqlalchemy.orm import Session  # Добавил Session для синхронной сессии
from sqlalchemy import create_engine

from src.core.config import settings  # Импортируем наши настройки

# Создаем асинхронный движок SQLAlchemy
async_engine = create_async_engine(
    str(settings.db.assembled_database_url),  # Используем обновленное поле из настроек
    echo=False,  # Можно сделать настраиваемым через settings, если нужно логирование SQL запросов
    # pool_pre_ping=True, # Полезно для долгоживущих соединений (проверяет соединение перед использованием)
    # pool_size=5, # Начальное количество соединений в пуле (можно вынести в settings.db.pool_size)
    # max_overflow=10, # Максимальное количество дополнительных соединений сверх pool_size (можно вынести в settings.db.max_overflow)
)

# Создаем фабрику для асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,  # Важно для асинхронного кода, чтобы объекты были доступны после коммита
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Зависимость FastAPI для получения асинхронной сессии базы данных.
    Гарантирует закрытие сессии после использования.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # Коммит и роллбэк лучше делать в бизнес-логике (репозитории, сервисы),
            # а не в самой зависимости. Зависимость должна предоставлять сессию.
            # await session.commit() # Пример, если бы коммит был здесь
        except Exception:
            await session.rollback()  # Откатываем транзакцию при любой ошибке
            raise
        # finally:
        # async with AsyncSessionLocal() менеджером контекста сессия закроется автоматически.
        # Явный session.close() здесь не обязателен и может быть избыточен.
        # await session.close()


def get_sync_database_url(db_url: str) -> str:
    if "+asyncpg" in db_url:
        return db_url.replace("+asyncpg", "")
    elif "+aiosqlite" in db_url:
        return db_url.replace("+aiosqlite", "")
    return db_url


SYNC_DATABASE_URL = get_sync_database_url(str(settings.db.assembled_database_url))

sync_engine = create_engine(SYNC_DATABASE_URL, echo=False)

SessionLocalSync = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


def get_sync_session() -> Generator[Session, None, None]:
    """Предоставляет синхронную сессию БД."""
    db_session = SessionLocalSync()
    try:
        yield db_session
        db_session.commit()
    except Exception:
        db_session.rollback()
        raise
    finally:
        db_session.close()
