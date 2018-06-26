"""
app.py

The application entry point.
"""
import argparse
import asyncio
import logging
from pathlib import Path

from aiohttp import os, web

from bonham.core.utils import opj
from .core.config import ApplicationConfig
from .core.security import check_retries_to, verify_start_permissions

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

__all__ = ['run']

parser = argparse.ArgumentParser(description='Start your Bonham app.')
parser.add_argument('--config', '-c', help='path to your config file')

log = logging.getLogger(__file__)

def run(config_path: str or Path = None, config: ApplicationConfig = None, retry: int = 0):
    if config is None:
        if config_path is None:
            config_path = opj(os.getcwd(), 'conf', 'app.conf.yaml')
            if not os.path.exists(config_path):
                raise ValueError(
                    "Couldn't get app configuration. Please provide a valid path to a config file or "
                    "ApplicationConfig.")
        config = ApplicationConfig(config_path)
    if config.DEBUG is not True:
        check_retries_to(config)
        if verify_start_permissions(config, retry) is False:
            run(config=config, retry=retry)
    runner = web.AppRunner(app)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(runner.setup())
    site = web.UnixSite(
        runner, path=config.SOCKETS_DIR,
        ssl_context=config.SSL_CONTEXT)
    loop.run_until_complete(site.start())
    try:
        loop.run_forever()
    except (KeyboardInterrupt, asyncio.CancelledError) as ex:
        log.info(f"")
        pass
    finally:
        loop.run_until_complete(runner.cleanup())
        loop.stop()
        loop.close()

if __name__ == '__main__':
    args = parser.parse_args()
    run(config=args.config)
