import asyncio
from argparse import ArgumentParser
from asyncio import Task, wait

import aiohttp_jinja2
import jinja2
from aiohttp import web
from uvloop import EventLoopPolicy

from bonham import db, logger, middlewares, router
from bonham.bonham_authentication import root as auth
from bonham.settings import DEBUG, TEMPLATE_DIR
from bonham.utils import prepared_uvloop

asyncio.set_event_loop_policy(EventLoopPolicy())

core_setup = [router, logger, db]

components = [auth]


async def setup_core(app):
    tasks = [app.loop.create_task(component.setup(app)) for component in core_setup]
    return await wait(tasks)


async def setup_components(app):
    tasks = [app.loop.create_task(component.setup(app)) for component in components]
    return await wait(tasks)


async def prepare_response(request, response):
    if 'assets' not in request.path:
        response.charset = 'utf-8'
        response.cookies.clear()


async def cancel_tasks():
    for task in Task.all_tasks():
        task.cancel()


async def shutdown(app: web.Application):
    print(f"shutdown app called.")
    for component in components:
        await component.shutdown(app)
    await app['db'].close()
    app['server'].close()
    await app['server'].wait_closed()
    await app['handler'].shutdown(60)
    await cancel_tasks()
    await app.shutdown()
    await app.cleanup()


async def on_startup(app: web.Application) -> None:
    print(f"startup called.\n\tapp: {app}", flush=True)


async def on_shutdown(app: web.Application) -> None:
    print(f"shutdown called.\n\tapp: {app}", flush=True)


async def on_cleanup(app: web.Application) -> None:
    print(f"startup called.\n\tapp: {app}", flush=True)

async def init_app(loop: asyncio.BaseEventLoop = None, port: int = None) -> web.Application:
    app = web.Application(middlewares=middlewares.all, loop=loop, debug=DEBUG)

    app['wss'] = {}

    # setup aiohttp_jinja2 template_engine
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(TEMPLATE_DIR))

    # parrallel setup of components
    await setup_core(app)
    await setup_components(app)

    app['handler'] = app.make_handler(
            secure_proxy_ssl_header=('X-FORWARDED-PROTO', 'https'),
            slow_request_timeout=20, debug=DEBUG)

    app['server'] = await loop.create_server(app['handler'], '127.0.1.2', port)

    app.logger.info(f"server running on port {port}\n\tserver: {app['server']}\n\thandler: {app['handler']}")
    return app


if __name__ == '__main__':
    parser = ArgumentParser('Run a Bonham Server instance on specified port.')
    parser.add_argument('port', type=int,
                        help='port number for this server instance, type integer e.g 8000')
    args = parser.parse_args()
    loop = prepared_uvloop(debug=DEBUG)
    app = loop.run_until_complete(init_app(loop=loop, port=args.port))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("keyboardInterrupt at root")
    finally:
        loop.run_until_complete(shutdown(app))
        loop.stop()
        loop.close()
