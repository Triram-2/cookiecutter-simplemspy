import asyncio
import pytest
from httpx import AsyncClient
from starlette import status

from {{cookiecutter.python_package_name}}.utils import (
    TASKS_ENDPOINT_PATH,
    TASKS_STREAM_NAME,
    statsd_client,
)

pytestmark = pytest.mark.asyncio


async def test_should_collect_duration_and_queue_size(
    async_client: AsyncClient, fake_redis
) -> None:
    statsd_client.reset()
    fake_redis.streams.clear()

    response = await async_client.post(
        TASKS_ENDPOINT_PATH, json={"data": "x", "metadata": {}}
    )
    await asyncio.sleep(0)

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert statsd_client.gauges["request_duration"] > 0
    assert statsd_client.gauges["task_queue_size"] == len(
        fake_redis.streams[TASKS_STREAM_NAME]
    )
