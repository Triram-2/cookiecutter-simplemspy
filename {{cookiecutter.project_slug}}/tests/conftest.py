import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Set environment variables for testing before importing settings.
# This ensures that test-specific configurations are loaded.
# For this template, we expect DB_DATABASE_URL to be "sqlite+aiosqlite:///:memory:"
# when running tests, which will override the URL assembly in DBSettings.
os.environ["DB_DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
# Set APP_ENV to 'test' to reflect in settings.
os.environ["APP_ENV"] = "test"


from name.api import app as fastapi_app
from name.core.config import settings
from name.db.base import Base
from name.db.database import get_async_session


# Test asynchronous engine for SQLite in-memory.
# The URL is taken from settings, which should now reflect DB_DATABASE_URL="sqlite+aiosqlite:///:memory:"
# or be assembled based on APP_ENV='test'.
test_engine = create_async_engine(
    str(settings.db.assembled_database_url),
    echo=False,  # Can be True for debugging SQL in tests
)

TestAsyncSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop(request) -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Provides an event loop for all tests in the session (auto mode for pytest-asyncio)."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(
    scope="function"
)  # Use function scope for DB isolation between tests
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Fixture to provide a test SQLite in-memory DB session."""
    async with test_engine.begin() as connection:
        # Create all tables before each test
        await connection.run_sync(Base.metadata.create_all)

    session = TestAsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()
        # Drop all tables after each test for complete isolation
        async with test_engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def override_get_async_session(
    db_session: AsyncSession,
) -> AsyncGenerator[None, None]:
    """Overrides the get_async_session dependency to use the test session."""

    async def _override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    fastapi_app.dependency_overrides[get_async_session] = _override_get_async_session
    yield
    del fastapi_app.dependency_overrides[get_async_session]


@pytest_asyncio.fixture(scope="function")
async def async_client(
    override_get_async_session: None,  # Ensures DB dependency is overridden
) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture to create an async HTTP client for API testing.
    Depends on override_get_async_session to ensure the DB dependency is overridden.
    """
    # Use FastAPI lifespan for proper app initialization and shutdown in tests
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app), base_url="http://testserver"
    ) as client:
        yield client
