import pytest
from httpx import AsyncClient
from starlette import status

from {{cookiecutter.python_package_name}}.utils import redis_stream, TASKS_STREAM_NAME

pytestmark = pytest.mark.asyncio


async def test_should_return_202_and_store_message(async_client: AsyncClient):
    redis_stream.streams.clear()
    payload = {"data": "hello", "metadata": {"foo": "bar"}}

    response = await async_client.post("/tasks", json=payload)

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert TASKS_STREAM_NAME in redis_stream.streams
    assert redis_stream.streams[TASKS_STREAM_NAME]
    message = redis_stream.streams[TASKS_STREAM_NAME][-1]
    assert message["payload"] == payload
