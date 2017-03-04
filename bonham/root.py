import aiohttp_jinja2
import asyncio
import asyncpg
import jinja2
import logging
from aiohttp import WSCloseCode, web
from bonham_authentication.middlewares import auth_middleware
from middlwares import data_middleware, engine_middleware, error_middleware
from uvloop import EventLoopPolicy

from bonham import router
from bonham.settings import DEBUG, DSN, LOG_FILE, LOG_FORMAT, LOG_LEVEL, TEMPLATE_DIR

asyncio.set_event_loop_policy(EventLoopPolicy())


async def startup(app):
    print(
            f"\nstartup called with ->\napp:\t{app.__dict__}\nhandler:\t{app['handler'].__dict__}\napp:\t{app["
            f"'server'].__dict__}")


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


async def init_app(loop=None) -> web.Application:
    # inititialize web.Application
    app = web.Application(middlewares=[
        engine_middleware,
        auth_middleware,
        data_middleware,
        error_middleware
    ], loop=loop, debug=DEBUG)

    # filling the router table
    await router.setup(app)

    # listening to app signals
    # app.on_startup.append(startup)
    # app.on_response_prepare.append(prepare_response)
    # app.on_cleanup.append(cleanup)

    # configure app logger
    app.logger = logging.getLogger('bonham.root')
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
    app['server'] = await loop.create_server(app['handler'], '127.0.0.1', 9090)
    print("server is up and running at localhost on port 9090.", flush=True)
    app.logger.debug(f"{'*'*10} server running at {app['server']} {'*'*10}")
    return app


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init_app(loop=loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(shutdown(app))
        loop.close()
