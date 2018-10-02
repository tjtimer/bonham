"""
test_app_setup.py
Tim "tjtimer" Jedro
01.10.2018
"""
from aiohttp import web

from bonham import app


async def test_setup():
    application = await app.setup()
    assert isinstance(application, web.Application)
