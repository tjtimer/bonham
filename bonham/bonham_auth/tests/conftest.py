# py.test fixtures

import pytest

from bonham.utils import prepared_uvloop


@pytest.fixture
def my_loop():
    loop = prepared_uvloop(debug=True)
    return loop

