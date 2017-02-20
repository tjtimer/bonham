# bonham/tests/conftest
# place py.test fixtures here

# if aiohttp.pytest_plugin is not installed, this provides the same functionality

import pytest

from bonham.db import Base, BaseModel
from bonham.root import create_app

pytest_plugins = 'aiohttp.pytest_plugin'


@pytest.fixture
def client(loop, test_client):
    app = create_app(loop=loop)
    return loop.run_until_complete(app)


class TestModel(Base, BaseModel):
    def __init__(self):
        super().__init__()


@pytest.fixture
def testmodel():
    return TestModel()
