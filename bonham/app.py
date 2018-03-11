"""
app.py

The application entry point.
"""
import argparse
import asyncio
import importlib
import logging.config
import os
import ssl
from _ssl import PROTOCOL_TLSv1_2

import aiohttp_jinja2
from aiohttp import web

from bonham.core.config import ApplicationConfig, load_config


try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

__all__ = ['run']

parser = argparse.ArgumentParser(description='Start your Bonham app.')
parser.add_argument('--config', '-c', help='path to your config file')


def init_logging_conf(config: str or dict):
    if isinstance(config, str):
        config = load_config(config)
    logging.config.dictConfig(config)


def import_apps(app_names: list or tuple):
    for name in app_names:
        yield name, importlib.import_module(f'.app', f'bonham.apps.{name}')


routes = web.RouteTableDef()
@routes.get('/')
async def index(request):
    return aiohttp_jinja2.render_template(
        'index', request, {'title': 'my app'})

def init_template_engine(app):
    aiohttp_jinja2.setup(
        app,
        loader=app['template_loader'](
            app['templates_path']
        )
    )

def get_ssl_context(*,
                    protocol=PROTOCOL_TLSv1_2,
                    purpose=ssl.Purpose.SERVER_AUTH, **kwargs) -> ssl.SSLContext:
    ssl_context = ssl.SSLContext(protocol=protocol)
    ssl_context.load_default_certs(purpose=purpose)
    def get_default():
        default_ciphers_list = [
            cipher['description'] for cipher in ssl_context.get_ciphers()
            if 'TLSv1.2' in cipher['description']
            ]
        return default_ciphers_list[0]
    ssl_context.set_ciphers(kwargs.pop('ciphers', get_default()))
    return ssl_context

def prepare_app(config_path: str):
    root = web.Application()
    root['config'] = ApplicationConfig(config_path)
    os.chdir(root['config']['directories']['application'])
    if root['config']['log'] is not None:
        init_logging_conf(root['config']['log'])
    for name, _app_ in import_apps(root['config']['directories']['apps']):
        app = web.Application()
        app.router.add_routes(getattr(_app_, 'routes', []))
        app.middlewares.append(getattr(_app_, 'middlewares', []))
        root.on_startup.append(getattr(_app_, 'on_startup', []))
        root.on_response_prepare.append(getattr(_app_, 'on_response_prepare', []))
        root.on_shutdown.append(getattr(_app_, 'on_shutdown', []))
        root.on_cleanup.append(getattr(_app_, 'on_cleanup', []))
        root.add_subapp(f"/{name}", app)
    if root['config']['template_loader'] is not False:
        init_template_engine(root)
    root.router.add_routes(routes)
    if root['config']['ssl'] is False:
        root['ssl_context'] = None
    else: root['ssl_context'] = get_ssl_context()
    return root

def run(app):
    loop = asyncio.get_event_loop()
    runner = web.AppRunner(app)
    loop.run_until_complete(runner.setup())
    site = web.UnixSite(
        runner, path=app['config']['directories']['sockets'],
        ssl_context=app['config']['ssl'])
    loop.run_until_complete(site.start())
    try:
        loop.run_forever()
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        loop.run_until_complete(runner.cleanup())
        loop.stop()
        loop.close()



if __name__ == '__main__':
    args = parser.parse_args()
    app = prepare_app(args.config)
    run(app)
