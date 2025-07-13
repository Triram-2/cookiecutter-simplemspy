import pytest
from httpx import AsyncClient
from starlette import status

from {{cookiecutter.python_package_name}}.utils import (
    TASKS_STREAM_NAME,
    statsd_client,
    tracer,
)

pytestmark = pytest.mark.asyncio


async def test_should_return_202_and_store_message(async_client: AsyncClient, fake_redis):
    fake_redis.streams.clear()
    statsd_client.reset()
    tracer.spans.clear()
    payload = {"data": "hello", "metadata": {"foo": "bar"}}

    response = await async_client.post("/tasks", json=payload)

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert TASKS_STREAM_NAME in fake_redis.streams
    assert fake_redis.streams[TASKS_STREAM_NAME]
    message = fake_redis.streams[TASKS_STREAM_NAME][-1]
    assert message["payload"] == payload
    assert statsd_client.counters["requests.tasks"] == 1
    assert tracer.spans and tracer.spans[-1].name == "create_task"


async def test_should_return_400_when_payload_invalid(async_client: AsyncClient):
    response = await async_client.post("/tasks", json={"foo": "bar"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_should_return_413_when_payload_too_large(async_client: AsyncClient):
    big_data = "x" * (1024 * 1024 + 1)
    response = await async_client.post(
        "/tasks",
        json={"data": big_data, "metadata": {}},
    )

    assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
