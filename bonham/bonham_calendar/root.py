from aiohttp import web

from .handler import create_calendar, get_calendars


async def setup_routes(router):
    router.add_post('/', create_calendar, name='create-calendar')
    router.add_get('/', get_calendars, name='get-calendars')


async def shutdown(app):
    print(f"\n\nshutting down calendar app")


async def setup(app):
    cal = web.Application(loop=app.loop)
    await setup_routes(cal.router)
    return app.add_subapp('/calendars', cal)
