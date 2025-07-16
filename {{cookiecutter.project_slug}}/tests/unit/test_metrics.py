import asyncio
import pytest

from {{cookiecutter.python_package_name}}.utils.metrics import AsyncStatsDClient


@pytest.mark.asyncio
async def test_should_apply_prefix_to_metric_name() -> None:
    messages: list[bytes] = []

    async def capture(self, message: bytes) -> None:
        messages.append(message)

    client = AsyncStatsDClient("localhost", 8125, prefix="pref")
    client._send = capture.__get__(client, AsyncStatsDClient)
    await client.incr("my.metric", 2)
    await client.gauge("another", 1.5)

    assert messages[0].startswith(b"pref.my.metric:2|c")
    assert messages[1].startswith(b"pref.another:1.5|g")
