import asyncio
import logging

import aiohttp_jinja2
import asyncpg
import jinja2
import uvloop
from aiohttp import web
from uvloop import EventLoopPolicy

from bonham import router
from bonham.bonham_authentication.middlewares import auth_middleware
from bonham.middlwares import data_middleware, engine_middleware, error_middleware
from bonham.settings import DEBUG, DSN, HOST, LOG_FILE, LOG_FORMAT, LOG_LEVEL, PORT, TEMPLATE_DIR

# Ultra fast implementation of asyncio event loop on top of libuv.
# see https://github.com/MagicStack/uvloop
asyncio.set_event_loop_policy(EventLoopPolicy())


async def init_app(loop=None):
    # init web.Application
    app = web.Application(middlewares=[
        auth_middleware,
        engine_middleware,
        data_middleware,
        error_middleware
    ], loop=loop, debug=DEBUG)
    app['db'] = await asyncpg.create_pool(dsn=DSN, loop=loop)
    # filling the router table
    router.setup(app.router)

    # configure app logger
    app.logger = logging.getLogger('bonham.root')
    formatter = logging.Formatter(LOG_FORMAT)
    log_file = logging.FileHandler(LOG_FILE)
    log_file.setFormatter(formatter)
    app.logger.setLevel(LOG_LEVEL)
    app.logger.addHandler(log_file)

    # init jinja2 template engine
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(TEMPLATE_DIR))

    # HTTP protocol factory for handling requests
    secure_proxy_ssl_header = ('X-Forwarded-Proto', 'https')
    app.make_handler(secure_proxy_ssl_header=secure_proxy_ssl_header)
    return app


def create_app(loop=None):
    if loop is None:
        loop = uvloop.new_event_loop()
        asyncio.set_event_loop(loop)
    app = loop.run_until_complete(init_app(loop=loop))
    app.logger.debug('started application')
    return app


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init_app(loop=loop))
    app.logger.debug(f'started application:\n\t{app.__dict__}')
    web.run_app(app, host=HOST, port=PORT)
