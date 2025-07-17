import json
from collections import defaultdict

import pytest

from {{cookiecutter.python_package_name}}.repository.redis_repo import RedisRepository
from {{cookiecutter.python_package_name}}.services.tasks_service import TasksService
from {{cookiecutter.python_package_name}}.utils import (
    TASKS_STREAM_NAME,
    DEAD_LETTER_STREAM_NAME,
    tracer,
)
from tests.conftest import FakeRedis


@pytest.mark.asyncio
async def test_enqueue_task_formats_and_stores_message() -> None:
    fake = FakeRedis()
    repo = RedisRepository(client=fake)
    service = TasksService(repo)

    payload = {"data": "x", "metadata": {"a": 1}}
    tracer.spans.clear()
    await service.enqueue_task(payload)

    assert TASKS_STREAM_NAME in fake.streams
    stored = fake.streams[TASKS_STREAM_NAME][0]
    assert json.loads(stored["payload"]) == payload
    assert "task_id" in stored
    assert "timestamp" in stored
    assert tracer.spans and tracer.spans[0].name == "постановка_задачи"


def test_calculate_metrics() -> None:
    tracer.spans.clear()
    avg, mn, mx = TasksService._calculate_metrics([1.0, 2.0, 3.0])
    assert avg == 2.0
    assert mn == 1.0
    assert mx == 3.0
    assert tracer.spans and tracer.spans[0].name == "расчет_метрик"


def test_calculate_metrics_empty_list() -> None:
    tracer.spans.clear()
    avg, mn, mx = TasksService._calculate_metrics([])
    assert avg == 0.0
    assert mn == 0.0
    assert mx == 0.0
    assert tracer.spans and tracer.spans[0].name == "расчет_метрик"


@pytest.mark.asyncio
async def test_should_report_average_min_max_metrics(monkeypatch) -> None:
    cpu_values = iter([10.0, 30.0])
    mem_values = iter([40.0, 50.0])

    class Mem:
        def __init__(self, percent: float) -> None:
            self.percent = percent


    monkeypatch.setattr(
        "{{cookiecutter.python_package_name}}.services.tasks_service.psutil.cpu_percent",
        lambda: next(cpu_values),
    )
    monkeypatch.setattr(
        "{{cookiecutter.python_package_name}}.services.tasks_service.psutil.virtual_memory",
        lambda: Mem(next(mem_values)),
    )
    monkeypatch.setattr(
        "{{cookiecutter.python_package_name}}.services.tasks_service.GPU_AVAILABLE",
        False,
    )

    gauges: dict[str, float] = {}

    async def fake_gauge(metric: str, value: float) -> None:
        gauges[metric] = value

    monkeypatch.setattr(
        "{{cookiecutter.python_package_name}}.services.tasks_service.statsd_client.gauge",
        fake_gauge,
    )

    fake = FakeRedis()
    repo = RedisRepository(client=fake)
    service = TasksService(repo)

    tracer.spans.clear()
    await service.enqueue_task({"data": 1})
    await service.enqueue_task({"data": 2})

    assert gauges["cpu.avg"] == 20.0
    assert gauges["cpu.min"] == 10.0
    assert gauges["cpu.max"] == 30.0
    assert gauges["mem.avg"] == 45.0
    assert gauges["mem.min"] == 40.0
    assert gauges["mem.max"] == 50.0
    assert [s.name for s in tracer.spans].count("постановка_задачи") == 2


class FailingRepo:
    def __init__(self, fail_times: int) -> None:
        self.fail_times = fail_times
        self.calls = 0
        self.streams: dict[str, list[dict]] = defaultdict(list)

    async def add_to_stream(self, stream_name: str, message: dict) -> str:
        self.calls += 1
        if self.calls <= self.fail_times:
            raise ConnectionError("down")
        self.streams[stream_name].append(message)
        return str(len(self.streams[stream_name]))


@pytest.mark.asyncio
async def test_should_retry_before_success(monkeypatch) -> None:
    repo = FailingRepo(fail_times=2)
    service = TasksService(repo)  # type: ignore[arg-type]

    sleeps: list[float] = []

    async def fake_sleep(delay: float) -> None:
        sleeps.append(delay)

    monkeypatch.setattr(
        "{{cookiecutter.python_package_name}}.services.tasks_service.asyncio.sleep",
        fake_sleep,
    )

    await service.enqueue_task({"data": 1})

    assert repo.calls == 3
    assert repo.streams[TASKS_STREAM_NAME]
    assert sleeps == [1, 2]


@pytest.mark.asyncio
async def test_should_send_to_dead_letter_after_retries(monkeypatch) -> None:
    repo = FailingRepo(fail_times=3)
    service = TasksService(repo)  # type: ignore[arg-type]

    monkeypatch.setattr(
        "{{cookiecutter.python_package_name}}.services.tasks_service.asyncio.sleep",
        lambda *_: None,
    )

    await service.enqueue_task({"data": 2})

    assert repo.calls == 4
    assert not repo.streams.get(TASKS_STREAM_NAME)
    assert repo.streams[DEAD_LETTER_STREAM_NAME]
