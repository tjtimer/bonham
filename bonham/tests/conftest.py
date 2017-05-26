# bonham/tests/conftest
# place py.test fixtures here

# if aiohttp.pytest_plugin is not installed, this provides the same functionality
import pytest

from bonham.models import Base, BaseModel
from bonham.utils import prepared_uvloop

pytest_plugins = 'aiohttp.pytest_plugin'


class TestModel(Base, BaseModel):
    pass


@pytest.fixture(scope='function')
def testmodel():
    return TestModel


@pytest.fixture(scope="function")
def my_loop():
    loop = prepared_uvloop(debug=True)
    return loop
