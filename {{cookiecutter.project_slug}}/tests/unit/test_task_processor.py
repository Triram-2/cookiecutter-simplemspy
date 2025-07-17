import asyncio
import json

import pytest

from {{cookiecutter.python_package_name}}.repository.redis_repo import RedisRepository
from {{cookiecutter.python_package_name}}.services.task_processor import TaskProcessor
from {{cookiecutter.python_package_name}}.utils import TASKS_STREAM_NAME, tracer
from tests.conftest import FakeRedis


@pytest.mark.asyncio
async def test_task_processor_handles_message() -> None:
    fake = FakeRedis()
    repo = RedisRepository(client=fake)
    await repo.add_to_stream(TASKS_STREAM_NAME, {"payload": json.dumps({"v": 1})})
    processor = TaskProcessor(repo)

    handled: list[dict] = []

    async def handle(fields: dict) -> None:
        handled.append(json.loads(fields["payload"]))

    processor.handle = handle  # type: ignore[assignment]

    tracer.spans.clear()
    await processor.start()
    await asyncio.sleep(0)  # allow processing
    await processor.stop()

    assert handled == [{"v": 1}]
    assert tracer.spans and tracer.spans[0].name == "обработка_задачи"
