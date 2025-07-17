import pytest
from httpx import AsyncClient
from starlette import status

from {{cookiecutter.python_package_name}}.utils import statsd_client, tracer

pytestmark = pytest.mark.asyncio


async def test_health_check(async_client: AsyncClient):
    """Tests the /health endpoint when Redis is reachable."""
    statsd_client.reset()
    tracer.spans.clear()

    response = await async_client.get("/health")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["status"] == "healthy"
    assert isinstance(data["timestamp"], str)
    assert isinstance(data["redis_connected"], bool)
    assert isinstance(data["version"], str) and data["version"]
    assert statsd_client.counters["requests.health"] == 1
    assert tracer.spans and tracer.spans[0].name == "проверка_здоровья"


async def test_should_return_503_when_redis_unavailable(
    async_client: AsyncClient, fake_redis, monkeypatch
):
    """Returns 503 when Redis ping fails."""
    async def fail_ping() -> bool:
        raise ConnectionError("redis down")

    monkeypatch.setattr(fake_redis, "ping", fail_ping)
    statsd_client.reset()
    tracer.spans.clear()

    response = await async_client.get("/health")

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    data = response.json()
    assert data["status"] == "unhealthy"
    assert data["redis_connected"] is False
    assert isinstance(data["timestamp"], str)
    assert isinstance(data["version"], str) and data["version"]
    assert statsd_client.counters["requests.health"] == 1
    assert tracer.spans and tracer.spans[0].name == "проверка_здоровья"
