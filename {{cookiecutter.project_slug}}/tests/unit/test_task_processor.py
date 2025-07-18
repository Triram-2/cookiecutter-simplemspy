import asyncio
import json

import pytest

from {{cookiecutter.python_package_name}}.repository.redis_repo import RedisRepository
from {{cookiecutter.python_package_name}}.services.task_processor import TaskProcessor
from {{cookiecutter.python_package_name}}.utils import (
    TASKS_STREAM_NAME,
    DEAD_LETTER_STREAM_NAME,
    tracer,
)
from tests.conftest import FakeRedis


@pytest.mark.asyncio
async def test_task_processor_handles_message() -> None:
    fake = FakeRedis()
    repo = RedisRepository(client=fake)
    await repo.add_to_stream(TASKS_STREAM_NAME, {"payload": json.dumps({"v": 1})})
    processor = TaskProcessor(repo)

    handled: list[dict] = []

    async def handle(fields: dict) -> None:
        with tracer.start_as_current_span("обработка_задачи"):
            handled.append(json.loads(fields["payload"]))

    processor.handle = handle  # type: ignore[assignment]

    tracer.spans.clear()
    await processor.start()
    await asyncio.sleep(0)  # allow processing
    await processor.stop()

    assert handled == [{"v": 1}]
    assert any(span.name == "обработка_задачи" for span in tracer.spans)


@pytest.mark.asyncio
async def test_task_processor_retries_and_dead_letter(monkeypatch) -> None:
    fake = FakeRedis()
    repo = RedisRepository(client=fake)
    await repo.add_to_stream(TASKS_STREAM_NAME, {"payload": json.dumps({"v": 2})})

    processor = TaskProcessor(repo)

    attempts: int = 0

    async def failing_handle(_: dict) -> None:
        nonlocal attempts
        attempts += 1
        raise RuntimeError("boom")

    async def fast_sleep(_: float) -> None:
        return None

    monkeypatch.setattr(
        "{{cookiecutter.python_package_name}}.services.task_processor.asyncio.sleep",
        fast_sleep,
    )

    processor.handle = failing_handle  # type: ignore[assignment]

    await processor.start()
    await asyncio.sleep(0)  # allow processing
    await processor.stop()

    assert attempts == 3
    assert fake.streams[DEAD_LETTER_STREAM_NAME]
