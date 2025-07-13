import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio


async def test_health_check(async_client: AsyncClient):
    """Tests the /health endpoint."""
    response = await async_client.get("/health")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["status"] == "healthy"
    assert isinstance(data["timestamp"], str)
    assert isinstance(data["redis_connected"], bool)
    assert isinstance(data["version"], str) and data["version"]
