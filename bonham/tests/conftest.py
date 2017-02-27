# bonham/tests/conftest
# place py.test fixtures here

# if aiohttp.pytest_plugin is not installed, this provides the same functionality
import asyncio

import pytest
import random
import uvloop

from bonham.db import Base, BaseModel
from bonham.root import create_app

pytest_plugins = 'aiohttp.pytest_plugin'


@pytest.fixture
def client(loop, test_client):
    app = create_app(loop=loop)
    return loop.run_until_complete(app)


class TestModel(Base, BaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@pytest.fixture(scope='function')
def testmodel():
    return TestModel


@pytest.fixture
def _id():
    return random.randint(1, 10000)


@pytest.fixture
def my_loop():
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = uvloop.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop
