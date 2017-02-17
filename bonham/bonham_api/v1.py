from aiohttp import web

from bonham.bonham_calendar.root import app as calendar
from bonham.bonham_user.root import app as user


def setup_routes(router):
    router.add_subapp('/users', user)
    router.add_subapp('/calendars', calendar)


app = web.Application()
setup_routes(app.router)
