# bonham/tests/conftest
# place py.test fixtures here

# if aiohttp.pytest_plugin is not installed, this provides the same functionality
import pytest

from bonham.db import Base, BaseModel
from bonham.utils import prepared_uvloop

pytest_plugins = 'aiohttp.pytest_plugin'


class TestModel(Base, BaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@pytest.fixture(scope='function')
def testmodel():
    return TestModel


@pytest.fixture
def my_loop():
    return prepared_uvloop(debug=True)
