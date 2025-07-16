import pytest

from {{cookiecutter.python_package_name}}.utils.circuitbreaker import (
    CircuitBreakerError,
)

from {{cookiecutter.python_package_name}}.repository.redis_repo import (
    RedisRepository,
)
from {{cookiecutter.python_package_name}}.utils import tracer
from tests.conftest import FakeRedis


@pytest.mark.asyncio
async def test_should_add_to_stream_and_ping() -> None:
    fake = FakeRedis()
    repo = RedisRepository(client=fake)
    tracer.spans.clear()
    await repo.add_to_stream("mystream", {"foo": "bar"})

    assert "mystream" in fake.streams
    assert fake.streams["mystream"][0]["foo"] == "bar"
    assert await repo.ping()
    assert [s.name for s in tracer.spans] == [
        "redis_add_to_stream",
        "redis_ping",
    ]


@pytest.mark.asyncio
async def test_should_open_breaker_after_failures() -> None:
    class FailingRedis(FakeRedis):
        def __init__(self, fail_times: int) -> None:
            super().__init__()
            self.fail_times = fail_times
            self.calls = 0

        async def xadd(self, stream_name: str, fields: dict, **_: dict) -> str:
            self.calls += 1
            if self.calls <= self.fail_times:
                raise ConnectionError("redis down")
            return await super().xadd(stream_name, fields)

    repo = RedisRepository(client=FailingRedis(fail_times=3))

    # first two calls fail but do not raise CircuitBreakerError
    tracer.spans.clear()
    for _ in range(2):
        with pytest.raises(ConnectionError):
            await repo.add_to_stream("s", {"foo": "bar"})

    # third call should trip the breaker
    with pytest.raises(CircuitBreakerError):
        await repo.add_to_stream("s", {"foo": "bar"})
    assert tracer.spans[-1].name == "circuitbreaker_call"
