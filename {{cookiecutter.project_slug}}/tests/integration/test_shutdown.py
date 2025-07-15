import pytest

from {{cookiecutter.python_package_name}}.api import app, health, tasks
from {{cookiecutter.python_package_name}}.utils import statsd_client, tracer
from tests.conftest import FakeRedis


class FakeRedisWithClose(FakeRedis):
    def __init__(self) -> None:
        super().__init__()
        self.closed = False
        self.waited = False

    async def close(self) -> None:
        self.closed = True

    async def wait_closed(self) -> None:
        self.waited = True


@pytest.mark.asyncio
async def test_should_flush_and_close_on_shutdown(monkeypatch) -> None:
    fake = FakeRedisWithClose()
    monkeypatch.setattr(health, "redis_repo", fake)
    monkeypatch.setattr(tasks.tasks_service, "repo", fake)

    await statsd_client.incr("test")
    with tracer.start_as_current_span("span"):
        pass

    await app.router.startup()
    await app.router.shutdown()

    assert fake.closed and fake.waited
    assert statsd_client.counters == {}
    assert statsd_client._transport is None
    assert tracer.spans == []
