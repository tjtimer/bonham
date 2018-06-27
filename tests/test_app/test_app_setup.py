# bonham test_app_setup
# created: 27.06.18
# Author: Tim "tjtimer" Jedro
# Email: tjtimer@gmail.com
from aiohttp import web

from bonham import app


def test_setup_without_params():
    application = app.setup()
    assert isinstance(application, web.Application)
