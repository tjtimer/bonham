from aiohttp import web

from .handler import create_calendar, get_calendars


async def setup_routes(router):
    router.add_post('/', create_calendar, name='create-calendar')
    router.add_get('/', get_calendars, name='get-calendars')


async def shutdown(app):
    print(f"\n\nCalendar shut down")


async def setup(app):
    cal = web.Application(loop=app.loop)
    await setup_routes(cal.router)
    app.add_subapp('/calendars', cal)
    return app
