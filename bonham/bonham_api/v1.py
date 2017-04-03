from aiohttp import web

from bonham.bonham_calendar.root import init_calendar
from bonham.bonham_profile.root import init_user


async def add_subapps(app):
    app.add_subapp('/users', await init_user(loop=app.loop))
    app.add_subapp('/calendars', await init_calendar(loop=app.loop))


async def init_api(loop=None):
    app = web.Application(loop=loop)
    await add_subapps(app)
    return app
