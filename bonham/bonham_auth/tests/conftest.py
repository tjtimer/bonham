# py.test fixtures
import asyncio

import pytest


@pytest.fixture
def my_loop():
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    return loop

