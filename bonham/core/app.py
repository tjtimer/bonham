"""

 app
"""
import os

import aiohttp_jinja2
from aiohttp import web

from bonham.core.config import ApplicationConfig, init_logging

routes = web.RouteTableDef()
app = web.Application()

@routes.get('/')
async def index(request):
    return await aiohttp_jinja2.render_template(
        'index', request, {'title': 'my app'})


def init_template_engine(app):
    aiohttp_jinja2.setup(
        app,
        loader=app['template_loader'](
            app['templates_path']
        )
    )


def prepare_subapp(_app_, root):
    app = web.Application()
    app.router.add_routes(getattr(_app_, 'routes', []))
    app.middlewares.append(getattr(_app_, 'middlewares', []))
    root.on_startup.append(getattr(_app_, 'on_startup', []))
    root.on_response_prepare.append(getattr(_app_, 'on_response_prepare', []))
    root.on_shutdown.append(getattr(_app_, 'on_shutdown', []))
    root.on_cleanup.append(getattr(_app_, 'on_cleanup', []))
    return app

def prepare_root(config_path: str):
    root = web.Application()
    root['config'] = ApplicationConfig(config_path)
    os.chdir(root['config']['directories']['application'])
    if root['config']['log'] is not None:
        init_logging(root['config']['log'])
    for _app_ in import_apps(root['config']):
        app = prepare_subapp(_app_, root)
        if hasattr(_app_, 'prepare'):
            _app_.prepare(app, root)
    if root['config']['template_loader'] is not False:
        init_template_engine(root)
        root.router.add_routes(routes)
    if root['config']['ssl'] is False:
        root['ssl_context'] = None
    else: root['ssl_context'] = get_ssl_context(root['config']['ssl'])
    return root
