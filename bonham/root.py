"""
    Bonham Root
    Author: Tim "tjtimer" Jedro
    version: 0.0.1dev

    Root provides the core capabilities for every Service
        -> read from and write to database
        -> sending emails (bonham_mail)
        -> identify the user (bonham_auth)

"""
import logging.config
from asyncio import Event, Task, gather
from pathlib import Path

import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp_swagger import setup_swagger

from bonham.bonham_auth import root as auth
from bonham.bonham_core import db, router
from bonham.bonham_core.middlewares import error_middleware
from bonham.bonham_core.sock import create_ssl_socket
from bonham.bonham_core.utils import load_yaml_conf, prepared_uvloop
from bonham.settings import APPLICATION_NAME, CONF_DIR, DEBUG, TEMPLATES_DIR

__all__ = [
    'Service'
    ]
logger_config = load_yaml_conf(Path(CONF_DIR).joinpath('logging.conf.yaml'))
logging.config.dictConfig(logger_config)
logger = logging.getLogger(__file__)

core = [db, router]
subapps = [auth]
middlewares = [error_middleware]


class Service(web.Application):
    _instance_count = 0

    def __init__(self):
        super().__init__(middlewares=middlewares)
        self._loop = prepared_uvloop(debug=DEBUG)
        self._ready = Event()
        self._stopped = Event()
        self._sock = create_ssl_socket(self._instance_count)
        self._handler = None
        self._server = None

        self.logger = logger
        self._loop.run_until_complete(self.setup())

        # init template render engine
        aiohttp_jinja2.setup(self, loader=jinja2.FileSystemLoader(TEMPLATES_DIR))
        setup_swagger(self)
        print(vars(self))

    @property
    def ready(self):
        return self._ready.is_set()

    @property
    def stopped(self):
        return self._stopped.is_set()

    async def setup_core(self):
        await gather(*(component.setup(self) for component in core))

    async def setup_subapps(self):
        await gather(*(subapp.setup(self) for subapp in subapps))

    @staticmethod
    async def cancel_tasks():
        for task in Task.all_tasks():
            task.cancel()

    async def shutdown(self):
        self.logger.info(
                f"\n\n{'*'*10} Shutting down {APPLICATION_NAME} instance {self._instance_count} {'*'*10}\n\n"
                )
        for subapp in subapps:
            await subapp.shutdown(self)
        for component in core:
            await component.shutdown(self)
        self._server.close()
        await self._server.wait_closed()
        await self._handler.shutdown(60)
        await self.cleanup()
        self.logger.info(
                f"\n\n{'*'*10} Successfully shut down {APPLICATION_NAME} instance {self._instance_count} {'*'*10}\n\n"
                )

    async def setup(self):
        await self.setup_core()
        await self.setup_subapps()

    def run(self):
        self._handler = self.make_handler(
                secure_proxy_ssl_header=('X-FORWARDED-PROTO', 'https'),
                slow_request_timeout=20)
        self._server = self._loop.run_until_complete(self._loop.create_server(self._handler, sock=self._sock))
        self._instance_count += 1
        self._ready.set()
        self.logger.info(
            f"\n\n{'*'*10} {APPLICATION_NAME} serving on : {self._server.sockets[0].getsockname()} {'*'*10}\n\n")
        try:
            self._loop.run_forever()
        except KeyboardInterrupt:
            print("\n\nKeyboardInterrupt at bonham root\n\n")
            pass
        except Exception as e:
            print(f"\n\n#########\nException at bonham root\n\n{type(e).__name__}: {e}")
            pass
        finally:
            self._loop.run_until_complete(self.shutdown())
            self._loop.run_until_complete(self._loop.shutdown_asyncgens())

        self._instance_count -= 1
        self._loop.stop()
        self._stopped.set()

if __name__ == '__main__':
    service = Service()
    service.run()
    print("end main")
