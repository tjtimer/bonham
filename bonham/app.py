# bonham app
# created: 27.06.18
# Author: Tim "tjtimer" Jedro
# Email: tjtimer@gmail.com
#
# try:
#     import uvloop
#     import asyncio
#
#     asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
# except ImportError:
#     pass
import logging

from aiohttp import web

logger = logging.getLogger('bonham')
logger.debug('my debug message')


async def setup():
    app = web.Application()
    return app
