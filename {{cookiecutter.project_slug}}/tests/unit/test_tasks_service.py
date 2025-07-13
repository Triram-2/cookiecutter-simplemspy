import pytest

from {{cookiecutter.python_package_name}}.repository.redis_repo import RedisRepository
from {{cookiecutter.python_package_name}}.services.tasks_service import TasksService
from {{cookiecutter.python_package_name}}.utils import TASKS_STREAM_NAME
from tests.conftest import FakeRedis


@pytest.mark.asyncio
async def test_enqueue_task_formats_and_stores_message() -> None:
    fake = FakeRedis()
    repo = RedisRepository(client=fake)
    service = TasksService(repo)

    payload = {"data": "x", "metadata": {"a": 1}}
    await service.enqueue_task(payload)

    assert TASKS_STREAM_NAME in fake.streams
    stored = fake.streams[TASKS_STREAM_NAME][0]
    assert stored["payload"] == payload
    assert "task_id" in stored
    assert "timestamp" in stored
