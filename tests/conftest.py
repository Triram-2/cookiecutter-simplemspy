# tests/conftest.py
import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Устанавливаем переменную окружения для указания тестового .env файла до импорта настроек
# Это один из способов гарантировать, что настройки загрузятся для тестов.
# Либо можно использовать pytest-dotenv и указать его в pytest.ini.
# В данном случае, мы будем полагаться на то, что DB_DATABASE_URL будет установлен
# в окружении запуска тестов (например, "sqlite+aiosqlite:///:memory:")
# или на логику в AppSettings, которая может выбрать тестовую БД по APP_ENV.

# Для простоты этого шаблона, мы ожидаем, что DB_DATABASE_URL будет "sqlite+aiosqlite:///:memory:"
# при запуске тестов, что переопределит сборку URL в DBSettings.
# Убедимся, что AppSettings использует это.
os.environ["DB_DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
# Также установим APP_ENV в 'test', чтобы это отражалось в настройках
os.environ["APP_ENV"] = "test"


from src.api import app as fastapi_app  # Приложение FastAPI
from src.core.config import settings  # Наши настройки
from src.db.base import Base  # Базовый класс для моделей SQLAlchemy
from src.db.database import get_async_session  # Оригинальная зависимость сессии


# Создаем тестовый асинхронный движок для SQLite in-memory
# URL берется из настроек, которые теперь должны учитывать DB_DATABASE_URL="sqlite+aiosqlite:///:memory:"
# или собирать его на основе APP_ENV='test'
test_engine = create_async_engine(
    str(settings.db.assembled_database_url),  # Используем собранный URL из настроек
    echo=False,  # Можно сделать True для отладки SQL в тестах
)

# Создаем фабрику для тестовых асинхронных сессий
TestAsyncSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop(request) -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Предоставляет event loop для всех тестов в сессии (режим auto для pytest-asyncio)."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(
    scope="function"
)  # Используем function scope для изоляции БД между тестами
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Фикстура для предоставления тестовой сессии БД SQLite in-memory."""
    async with test_engine.begin() as connection:
        # Создаем все таблицы перед каждым тестом
        await connection.run_sync(Base.metadata.create_all)

    session = TestAsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()
        # Удаляем все таблицы после каждого теста для полной изоляции
        async with test_engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def override_get_async_session(
    db_session: AsyncSession,
) -> AsyncGenerator[None, None]:
    """Переопределяет зависимость get_async_session на использование тестовой сессии."""

    async def _override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    fastapi_app.dependency_overrides[get_async_session] = _override_get_async_session
    yield
    # Возвращаем оригинальную зависимость после теста, если это необходимо
    # или просто очищаем оверрайды, если приложение пересоздается для каждого теста/модуля
    del fastapi_app.dependency_overrides[get_async_session]


@pytest_asyncio.fixture(scope="function")
async def async_client(
    override_get_async_session: None,
) -> AsyncGenerator[AsyncClient, None]:
    """
    Фикстура для создания асинхронного HTTP клиента для тестирования API.
    Зависит от override_get_async_session, чтобы убедиться, что зависимость БД переопределена.
    """
    # Используем lifespan FastAPI для корректной инициализации и завершения приложения в тестах
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app), base_url="http://testserver"
    ) as client:
        yield client


# Если бы мы не использовали override_get_async_session как зависимость для async_client,
# а хотели бы, чтобы приложение создавалось с оверрайдом один раз на модуль или сессию:
# @pytest.fixture(scope="module") # или "session"
# def test_app_with_overrides():
#     async def _override_get_async_session_module_scope():
#          # Здесь логика получения сессии для такого скоупа, может быть сложнее
#         session = TestAsyncSessionLocal()
#         try:
#             yield session
#         finally:
#             await session.close()

#     fastapi_app.dependency_overrides[get_async_session] = _override_get_async_session_module_scope
#     yield fastapi_app # Возвращаем сам app
#     del fastapi_app.dependency_overrides[get_async_session]

# @pytest_asyncio.fixture(scope="module")
# async def async_client_module_scope(test_app_with_overrides) -> AsyncGenerator[AsyncClient, None]:
#     async with AsyncClient(app=test_app_with_overrides, base_url="http://testserver") as client:
#         yield client
