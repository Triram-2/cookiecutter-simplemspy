import pytest

from {{cookiecutter.python_package_name}}.repository.redis_repo import RedisRepository
from tests.conftest import FakeRedis


@pytest.mark.asyncio
async def test_should_add_to_stream_and_ping() -> None:
    fake = FakeRedis()
    repo = RedisRepository(client=fake)

    await repo.add_to_stream("mystream", {"foo": "bar"})

    assert "mystream" in fake.streams
    assert fake.streams["mystream"][0]["foo"] == "bar"
    assert await repo.ping()
