# bonham/tests/conftest
# place py.test fixtures here

# if aiohttp.pytest_plugin is not installed, this provides the same
# functionality
import pytest

from bonham.bonham_core.db import create_tables
from bonham.bonham_core.helper import BLoop
from bonham.bonham_core.models import Base, BaseModel

pytest_plugins = 'aiohttp.pytest_plugin'


class TestModel(Base, BaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@pytest.fixture(scope='function')
def testmodel():
    return TestModel


@pytest.fixture(scope="function")
def my_loop():
    loop = BLoop(debug=True)
    return loop


create_tables(models=(TestModel,))
