# src/db/database.py
"""
Модуль для настройки подключения к базе данных с использованием SQLAlchemy.
Предоставляет асинхронный движок (engine) и фабрику сессий.
"""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker # Для возможного использования синхронных частей, если потребуется
from typing import AsyncGenerator, Generator # Добавил Generator для синхронной сессии
from sqlalchemy.orm import Session # Добавил Session для синхронной сессии

from src.core.config import settings # Импортируем наши настройки

# Создаем асинхронный движок SQLAlchemy
# Мы уверены, что settings.db.database_url уже корректно сформирован Pydantic моделью
async_engine = create_async_engine(
    str(settings.db.database_url), # Pydantic может вернуть PostgresDsn, приводим к строке
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
    expire_on_commit=False, # Важно для асинхронного кода, чтобы объекты были доступны после коммита
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
            await session.rollback() # Откатываем транзакцию при любой ошибке
            raise
        # finally:
            # async with AsyncSessionLocal() менеджером контекста сессия закроется автоматически.
            # Явный session.close() здесь не обязателен и может быть избыточен.
            # await session.close() 

# --- Пример синхронного движка и сессий для Alembic или других синхронных задач ---
# Alembic работает с синхронным кодом SQLAlchemy.
# Важно: URL для синхронного движка должен быть без суффиксов +asyncpg или +aiosqlite.

# from sqlalchemy import create_engine

# def get_sync_database_url(db_url: str) -> str:
#     """Преобразует асинхронный URL в синхронный для Alembic."""
#     if "+asyncpg" in db_url:
#         return db_url.replace("+asyncpg", "")
#     elif "+aiosqlite" in db_url:
#         return db_url.replace("+aiosqlite", "")
#     # Добавьте другие асинхронные драйверы, если используете
#     return db_url

# SYNC_DATABASE_URL = get_sync_database_url(str(settings.db.database_url))

# sync_engine = create_engine(SYNC_DATABASE_URL, echo=False)

# SessionLocalSync = sessionmaker(
#     autocommit=False, 
#     autoflush=False, 
#     bind=sync_engine
# )

# def get_sync_session() -> Generator[Session, None, None]:
#     """
#     Генератор для получения синхронной сессии базы данных.
#     """
#     db_session = SessionLocalSync()
#     try:
#         yield db_session
#         db_session.commit() # Опционально: коммит по завершению успешной работы
#     except Exception:
#         db_session.rollback()
#         raise
#     finally:
#         db_session.close()

# Для использования в Alembic (например, в env.py):
# from src.db.database import SYNC_DATABASE_URL
# config.set_main_option('sqlalchemy.url', SYNC_DATABASE_URL)
# или
# from src.db.database import sync_engine
# connection = sync_engine.connect()
# context.configure(connection=connection, target_metadata=target_metadata)
# try:
#   ...
# finally:
#   connection.close()

# Логгер для этого модуля (если потребуется специфическое логирование)
# from src.core import get_logger
# log = get_logger(__name__)
# log.info("Модуль database.py загружен, асинхронный движок и фабрика сессий созданы.")
