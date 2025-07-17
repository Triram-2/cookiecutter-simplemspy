import asyncio
import uvloop
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from starlette.routing import Router

# Ensure test environment
# Pydantic settings use the ``APP_`` prefix so we need ``APP_APP_ENV``
os.environ["APP_APP_ENV"] = "test"

from {{cookiecutter.python_package_name}}.api import app as fastapi_app
from {{cookiecutter.python_package_name}}.api import health, tasks, main as api_main
from {{cookiecutter.python_package_name}}.middleware import MetricsMiddleware
from {{cookiecutter.python_package_name}} import utils
from {{cookiecutter.python_package_name}}.core.config import settings
from collections import defaultdict


class FakeRedis:
    def __init__(self) -> None:
        self.streams = defaultdict(list)
        self.groups = defaultdict(lambda: defaultdict(int))

    async def xadd(self, stream_name: str, fields: dict, **_: dict) -> str:
        self.streams[stream_name].append(fields)
        return str(len(self.streams[stream_name]))

    async def add_to_stream(self, stream_name: str, message: dict) -> str:
        return await self.xadd(stream_name, message)

    async def ping(self) -> bool:
        return True

    async def create_group(self, stream_name: str) -> None:
        await self.xgroup_create(stream_name, settings.redis.consumer_group)

    async def fetch(
        self, stream_name: str, count: int = 1, block_ms: int = 1000
    ) -> list[tuple[str, dict]]:
        result = await self.xreadgroup(
            settings.redis.consumer_group,
            settings.redis.consumer_name,
            streams={stream_name: ">"},
            count=count,
            block=block_ms,
        )
        messages: list[tuple[str, dict]] = []
        for _stream, msgs in result:
            for msg_id, data in msgs:
                messages.append((msg_id, data))
        return messages

    async def ack(self, stream_name: str, message_id: str) -> int:
        return await self.xack(
            stream_name, settings.redis.consumer_group, message_id
        )

    async def xgroup_create(self, stream_name: str, group_name: str, **_: dict) -> None:
        self.groups[stream_name][group_name] = 0

    async def xreadgroup(
        self,
        group_name: str,
        consumer_name: str,
        streams: dict,
        count: int = 1,
        block: int | None = None,
    ) -> list[tuple[str, list[tuple[str, dict]]]]:
        stream_name = next(iter(streams))
        index = self.groups[stream_name][group_name]
        if index >= len(self.streams[stream_name]):
            await asyncio.sleep(0)
            return []
        messages = self.streams[stream_name][index : index + count]
        self.groups[stream_name][group_name] += len(messages)
        return [
            (
                stream_name,
                [(str(i + 1), msg) for i, msg in enumerate(messages, start=index)],
            )
        ]

    async def xack(self, stream_name: str, group_name: str, message_id: str) -> int:
        return 1

    async def xlen(self, stream_name: str) -> int:
        return len(self.streams[stream_name])


@pytest_asyncio.fixture(autouse=True)
async def fake_redis(monkeypatch) -> AsyncGenerator[FakeRedis, None]:
    fake = FakeRedis()
    monkeypatch.setattr(health, "redis_repo", fake)
    health.router = health.get_router(fake)
    monkeypatch.setattr(tasks.tasks_service, "repo", fake)
    api_main.router = Router()
    api_main.router.routes.extend(health.router.routes)
    api_main.router.routes.extend(tasks.router.routes)
    fastapi_app.router.routes = list(api_main.router.routes)
    for mw in fastapi_app.user_middleware:
        if mw.cls is MetricsMiddleware:
            if hasattr(mw, "options"):
                mw.options["repo"] = fake
            else:
                mw.kwargs["repo"] = fake
    fastapi_app.middleware_stack = fastapi_app.build_middleware_stack()
    yield fake


@pytest_asyncio.fixture(autouse=True)
async def stub_statsd(monkeypatch) -> AsyncGenerator[None, None]:
    async def noop(_: bytes) -> None:
        return None

    monkeypatch.setattr(utils.statsd_client, "_send", noop)
    yield


@pytest.fixture(scope="session")
def event_loop(request) -> Generator[asyncio.AbstractEventLoop, None, None]:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app), base_url="http://testserver"
    ) as client:
        yield client
