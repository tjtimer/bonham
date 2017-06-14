"""
    Bonham Root
    Author: Tim "tjtimer" Jedro
    version: 0.0.1dev

    Root provides the core capabilities for every Service
        -> read from and write to database
        -> sending emails (bonham_mail)
        -> identify the user (bonham_auth)

"""
import asyncio
import logging
import logging.config
import os
import socket
from argparse import ArgumentParser
from asyncio import Event, Task, gather
from pathlib import Path

import aiohttp_jinja2
import jinja2
import yaml
from aiohttp import web
from uvloop import EventLoopPolicy

from bonham import db, router
from bonham.bonham_auth import root as auth
from bonham.middlewares import *
from bonham.settings import DEBUG, SOCKET_FILE, TEMPLATE_DIR
from bonham.utils import prepared_uvloop

# use uvloop
asyncio.set_event_loop_policy(EventLoopPolicy())

parser = ArgumentParser('Run a Bonham app instance on specified port.')
parser.add_argument('port', type=int, help='port number for this server instance, type integer e.g 8000')

core = [db, router]
subapps = [auth]
middlewares = [error_middleware, db_middleware, query_string_middleware, data_middleware]

async def setup_core(app):
    await gather(*(component.setup(app) for component in core))


async def setup_subapps(app):
    await gather(*(subapp.setup(app) for subapp in subapps))


def setup_logging(path: Path=None):
    """
        Setup logging configuration
    """
    if path is None:
        path = os.path.join(os.path.dirname(__file__), 'logging.conf.yaml')
    path = path
    with open(path, 'r') as f:
        config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)


async def prepare_response(request, response):
    response.charset = 'utf-8'


def prepare_socket(port: int) -> socket:
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setblocking(0)
    sock_file = f"{SOCKET_FILE}_{port}.sock"
    if os.path.exists(sock_file):
        os.remove(sock_file)
    sock.bind(sock_file)
    os.chmod(sock_file, 666)
    return sock


async def cancel_tasks():
    for task in Task.all_tasks():
        task.cancel()


async def shutdown(app):
    app.logger.info(f"\n\n{'*'*10} Shutting down Bonham App Server instance {'*'*10}\n\n")
    for subapp in subapps:
        await subapp.shutdown(app)
    for component in core:
        await component.shutdown(app)
    if 'server' in app.keys():
        app['server'].close()
        await app['server'].wait_closed()
        await app['handler'].shutdown(60)
    await app.cleanup()
    app.stopped.set()
    app.logger.info(f"\n\n{'*'*10} Successfully shut down Bonham App Server instance {'*'*10}\n\n")


async def setup(loop: asyncio.BaseEventLoop = None, sock: socket = None) -> web.Application:
    app = web.Application(middlewares=middlewares, loop=loop, debug=DEBUG)
    app.ready = Event()
    app.stopped = Event()
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(TEMPLATE_DIR))
    app.on_shutdown.append(shutdown)

    await setup_core(app)
    await setup_subapps(app)

    app['handler'] = app.make_handler(
            secure_proxy_ssl_header=('X-FORWARDED-PROTO', 'https'),
            slow_request_timeout=20)
    app['server'] = await loop.create_server(app['handler'], sock=sock)
    return app


def run():
    setup_logging()
    args = parser.parse_args()
    sock = prepare_socket(args.port)
    loop = prepared_uvloop(debug=DEBUG)
    app = loop.run_until_complete(setup(loop=loop, sock=sock))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("\n\nKeyboardInterrupt at bonham root\n\n")
        pass
    except Exception as e:
        print(f"\n\n#########\nException at bonham root\n\n{type(e).__name__}")
        pass
    finally:
        loop.run_until_complete(app.shutdown())
        loop.run_until_complete(loop.shutdown_asyncgens())
    loop.stop()
    loop.close()
    return True


if __name__ == '__main__':
    run()
