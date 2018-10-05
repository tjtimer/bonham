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
import asyncio
import enum
import importlib
import logging
from pathlib import Path

from aiohttp import web

logger = logging.getLogger('bonham')
logger.debug('my debug message')

APP_DIR = Path(__file__).parent
SERVICE_DIR = APP_DIR / 'service'
SERVICES = {importlib.import_module(f'{APP_DIR.name}.{SERVICE_DIR.name}.{srv.stem}')
            for srv in SERVICE_DIR.glob('*py')
            if '__' not in srv.stem}


class AccessType(enum.Enum):
    """access permissions
    (e.g. database collections, endpoints, files, ...)
    """
    NULL = 0
    READ = 1
    UPDATE = 2
    FULL = 3


class IsAdminOf('Edge'):
    pass


class IsMemberOf('Edge'):
    pass


async def setup():
    app = web.Application()
    await asyncio.gather(
        *(srv.setup(app) for srv in SERVICES if hasattr(srv, 'setup'))
    )
    return app


def run():
    asyncio.get_event_loop().run_until_complete(setup())
    print('setup done!')