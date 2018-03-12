"""
app.py

The application entry point.
"""
import argparse
import asyncio

from aiohttp import web

from bonham.core.app import prepare_root


try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

__all__ = ['run']

parser = argparse.ArgumentParser(description='Start your Bonham app.')
parser.add_argument('--config', '-c', help='path to your config file')


def run(*, config: str=None, app: web.Application=None):
    if app is None:
        app = prepare_root(config)
    loop = asyncio.get_event_loop()
    runner = web.AppRunner(app)
    loop.run_until_complete(runner.setup())
    site = web.UnixSite(
        runner, path=app['config']['directories']['sockets'],
        ssl_context=app['config']['ssl'])
    loop.run_until_complete(site.start())
    try:
        loop.run_forever()
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        loop.run_until_complete(runner.cleanup())
        loop.stop()
        loop.close()


if __name__ == '__main__':
    args = parser.parse_args()
    run(config=args.config)
