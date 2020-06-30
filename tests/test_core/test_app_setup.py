"""
bonham

test_app_setup

Author: Tim "tjtimer" Jedro
Email: tjtimer@gmail.com
created: 30.06.20
"""
from aiohttp import web

from bonham.core import app


def test_app_setup_returns_app():
    result = app.setup()
    assert isinstance(result, web.Application)