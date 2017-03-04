from aiohttp import web

from bonham.bonham_calendar.handler import get_calendars


async def setup_routes(router):
    router.add_get('/calendars/', get_calendars, name='get-calendars')


async def init_calendar(loop=None):
    app = web.Application(loop=loop)
    await setup_routes(app.router)
    return app
