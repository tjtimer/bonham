"""

 app
"""
import importlib
import logging.config
import os
import ssl
from _ssl import PROTOCOL_TLSv1_2

import aiohttp_jinja2
from aiohttp import web

from bonham.core.config import load_config, ApplicationConfig


def init_logging_conf(config: str or dict):
    if isinstance(config, str):
        config = load_config(config)
        logging.config.dictConfig(config)
    elif isinstance(config, dict):
        if 'type' not in config.keys():
            logging.config.dictConfig(config)
        elif config['type'] == 'ini':
            logging.config.fileConfig(config['path'])
        else:
            logging.config.listen(config['port'], verify=True)


def import_apps(config: dict):
    directory = config['directories']['apps']
    yield (importlib.import_module(f'.app', f'{directory}.{name}')
           for name in os.listdir(directory)
           if name not in config.get('blacklisted_apps', []))


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


def get_default_ciphers(ssl_context, versions=None):
    if not isinstance(versions, (list, tuple)):
        versions = ['TLSv1.1', 'TLSv1.2']
    default_ciphers_list = [
        cipher['description'] for cipher in ssl_context.get_ciphers()
        if any([version in cipher['description']
                for version in versions])
        ]
    return default_ciphers_list

def get_ssl_context(config, *,
                    protocol=PROTOCOL_TLSv1_2,
                    purpose=ssl.Purpose.SERVER_AUTH, **kwargs) -> ssl.SSLContext:
    ssl_context = ssl.SSLContext(protocol=protocol)
    ssl_context.load_default_certs(purpose=purpose)
    ciphers = kwargs.pop(
        'ciphers', get_default_ciphers(ssl_context, config))
    ssl_context.set_ciphers(ciphers)
    return ssl_context

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
        init_logging_conf(root['config']['log'])
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
