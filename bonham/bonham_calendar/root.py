from aiohttp import web

from bonham.bonham_calendar.handler import get_calendars


def setup_routes(router):
    router.add_get('/calendars/', get_calendars, name='get-calendars')


app = web.Application()
setup_routes(app.router)
