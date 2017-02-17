import asyncio

import pytest
from aiopg.sa import create_engine

from bonham.bonham_user.models import User
from bonham.settings import DSN


@pytest.fixture
def create_request(request):
    @asyncio.coroutine
    def req(_request):
        print(_request)
        _request['user'] = User()
        engine = yield from create_engine(DSN)
        connection = yield from engine.acquire()
        _request['connection'] = connection
        return _request

    return req
