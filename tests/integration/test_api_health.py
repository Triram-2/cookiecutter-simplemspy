# tests/integration/test_api_health.py
import pytest
from httpx import AsyncClient
from starlette import status  # Для использования именованных кодов статуса

# Помечаем все тесты в этом модуле как асинхронные
pytestmark = pytest.mark.asyncio


async def test_health_check(async_client: AsyncClient):
    """Тестирует эндпоинт проверки работоспособности /api/v1/health."""
    response = await async_client.get("/api/v1/health")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "healthy"}
