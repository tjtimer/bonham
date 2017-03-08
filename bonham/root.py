import asyncio
from asyncio import Task

import aiohttp_jinja2
import asyncpg
import jinja2
import logging
from aiohttp import WSCloseCode, web
from uvloop import EventLoopPolicy

from bonham import router
from bonham.bonham_authentication.middlewares import auth_middleware
from bonham.middlwares import data_middleware, engine_middleware, error_middleware
from bonham.settings import DEBUG, DSN, LOG_FILE, LOG_FORMAT, LOG_LEVEL, TEMPLATE_DIR
from bonham.utils import prepared_uvloop

asyncio.set_event_loop_policy(EventLoopPolicy())


async def prepare_response(request, response):
    if 'assets' not in request.path:
        response.charset = 'utf-8'
        response.cookies.clear()


async def shutdown(app: web.Application):
    app['server'].close()
    await app['db'].close()
    for key, ws in app['wss'].items():
        await ws.close(code=WSCloseCode.GOING_AWAY,
                       message='Server shutdown')
        del app['wss'][key]
    await app['server'].wait_closed()
    await app.shutdown()
    await app['handler'].shutdown(60)
    await app.cleanup()
    for task in Task.all_tasks():
        task.cancel()
    loop.stop()


async def init_app(loop: asyncio.BaseEventLoop = None, port: int = None) -> web.Application:
    # inititialize web.Application
    app = web.Application(middlewares=[
        engine_middleware,
        auth_middleware,
        data_middleware,
        error_middleware
    ], loop=loop, debug=DEBUG)
    if port is None:
        port = 9091
    # filling the router table
    await router.setup(app)

    # listening to app signals
    # app.on_startup.append(startup)
    # app.on_response_prepare.append(prepare_response)
    # app.on_cleanup.append(cleanup)

    # configure app logger
    app.logger = logging.getLogger('bonham.server')
    formatter = logging.Formatter(LOG_FORMAT)
    log_file = logging.FileHandler(LOG_FILE)
    log_file.setFormatter(formatter)
    app.logger.setLevel(LOG_LEVEL)
    app.logger.addHandler(log_file)

    # init jinja2 template engine
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(TEMPLATE_DIR))

    app['db'] = await asyncpg.create_pool(dsn=DSN, loop=loop, command_timeout=60)
    app['wss'] = { }
    app['auth_users'] = { }
    # HTTP protocol factory for handling requests
    secure_proxy_ssl_header = ('X-FORWARDED-FOR', 'https')
    app['handler'] = app.make_handler(secure_proxy_ssl_header=secure_proxy_ssl_header)
    app['server'] = await loop.create_server(app['handler'], 'localhost', port)
    print(f"server is now running at localhost on port {port}.", flush=True)
    app.logger.debug(f"{'*'*10} server is running {'*'*10}\n\tserver: {app['server']}\n\thandler: {app['handler']}")
    return app


if __name__ == '__main__':
    loop = prepared_uvloop(debug=DEBUG)
    app = loop.run_until_complete(init_app(loop=loop, port=9090))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("keyboardInterrupt at root")
        pass
    finally:
        loop.run_until_complete(shutdown(app))
        loop.stop()
        loop.close()
