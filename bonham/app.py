# bonham app
# created: 27.06.18
# Author: Tim "tjtimer" Jedro
# Email: tjtimer@gmail.com
import aiohttp_jinja2 as aiohttp_jinja2
import jinja2
from aiohttp import web

from bonham.config import AppConfig

routes = web.RouteTableDef()
app = web.Application()


def setup():
    app['config'] = AppConfig()
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(app['config']['template_dir']))
    app.add_routes(routes)
    return app


def run(**kwargs):
    web.run_app(app, **kwargs)

if __name__ == '__main__':
    run()
