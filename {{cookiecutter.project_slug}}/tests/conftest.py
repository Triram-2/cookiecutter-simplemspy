import asyncio
import uvloop
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from starlette.routing import Router

# Ensure test environment
os.environ["APP_ENV"] = "test"

from {{cookiecutter.python_package_name}}.api import app as fastapi_app
from {{cookiecutter.python_package_name}}.api import health, tasks, main as api_main
from {{cookiecutter.python_package_name}} import utils
from collections import defaultdict


class FakeRedis:
    def __init__(self) -> None:
        self.streams = defaultdict(list)

    async def xadd(self, stream_name: str, fields: dict, **_: dict) -> str:
        self.streams[stream_name].append(fields)
        return str(len(self.streams[stream_name]))

    async def add_to_stream(self, stream_name: str, message: dict) -> str:
        return await self.xadd(stream_name, message)

    async def ping(self) -> bool:
        return True


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
