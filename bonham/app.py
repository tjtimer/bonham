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
import jinja2
from aiohttp import web


try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

from bonham.core import pg_db
from bonham.core.utils import load_yaml_conf

__all__ = ['run']

parser = argparse.ArgumentParser(description='Start your Bonham app.')
parser.add_argument('--config', '-c', help='path to your config file')


def load_config(path: str)->dict:
    app_conf = os.path.join(path, 'app.conf.yaml')
    local_conf = os.path.join(path, 'local.conf.yaml')
    config = load_yaml_conf(app_conf)
    config.update(**load_yaml_conf(local_conf))
    return config


def init_logger(path: str):
    logger_config = load_yaml_conf(path)
    logging.config.dictConfig(logger_config)
    logger = logging.getLogger(__file__)
    return logger


def import_apps(app_names: list or tuple):
    for name in app_names:
        yield name, importlib.import_module(f'.app', f'bonham.apps.{name}')


def bind_models(models, engine):
    for model in models:
        model.metadata.bind = engine
        model.metadata.create_all()


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

def run(config_path: str):
    root = web.Application()
    root['config'] = load_config(config_path)
    root.logger = init_logger(
        os.path.join(
            root['config']['server_root'],
            root['config']['logging_conf']
        ))
    pg_alchemy = pg_db.get_alchemy_engine(root['config']['dsn'])
    for name, _app_ in import_apps(root['config']['installed_apps']):
        bind_models(getattr(_app_, 'models', []), pg_alchemy)
        app = web.Application()
        app.router.add_routes(getattr(_app_, 'routes', []))
        app.middlewares.append(getattr(_app_, 'middlewares', []))
        root.on_startup.append(getattr(_app_, 'on_startup', []))
        root.on_response_prepare.append(getattr(_app_, 'on_response_prepare', []))
        root.on_shutdown.append(getattr(_app_, 'on_shutdown', []))
        root.on_cleanup.append(getattr(_app_, 'on_cleanup', []))
        root.add_subapp(f"/{name}", app)
    init_template_engine(root)
    root.router.add_routes(routes)
    loop = asyncio.get_event_loop()
    runner = web.AppRunner(root)
    loop.run_until_complete(runner.setup())
    site = web.UnixSite(
        runner, path=os.path.join(
            root['config']['server_root'],
            root['config']['sock_dir']),
        ssl_context=get_ssl_context())
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
    run(args.config)
