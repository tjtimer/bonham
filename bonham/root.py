import asyncio
import logging
import os
import sys

import aiohttp_jinja2 as aiohttp_jinja2
import jinja2 as jinja2
import uvloop
from aiohttp import web

# this adds our project folder to the python path
# needed to import from bonham
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

from bonham.settings import INSTALLED_MIDDLEWARES, DEBUG, TEMPLATE_DIR, LOG_FORMAT, LOG_FILE, LOG_LEVEL

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def init_app(loop=None):
    # init web.Application
    app = web.Application(loop=loop, middlewares=INSTALLED_MIDDLEWARES, debug=DEBUG)

    # configure app logger
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


if __name__ == '__main__':
    app = init_app()
    app.logger.debug('started application')
    web.run_app(app)
