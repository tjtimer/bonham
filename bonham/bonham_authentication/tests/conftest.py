# py.test fixtures
import asyncio

import pytest
import uvloop


@pytest.fixture
def my_loop():
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = uvloop.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop
