"""
bonham/bonham_core/service.py

Author: Tim "tjtimer" Jedro

Version: 0.0.1dev
"""

import asyncio
import logging.config
import traceback
from pathlib import Path

import aiohttp_jinja2
import arrow
import jinja2
import uvloop
from aiohttp import web
from aiohttp.signals import Signal
from aiohttp.web_exceptions import HTTPFound, HTTPNotFound

from bonham.bonham_core.channels import Channel
from bonham.bonham_core.exceptions import RequestDenied
from bonham.bonham_core.helper import BLoop, load_yaml_conf
from bonham.settings import (
    CONF_DIR, DEBUG, HOST, PORT, TEMPLATES_DIR
    )

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

logger_config = load_yaml_conf(Path(CONF_DIR).joinpath('logging.conf.yaml'))
logging.config.dictConfig(logger_config)
logger = logging.getLogger(__name__)

__all__ = ('Service',)


class Service(web.Application):
    """
    Bonham Service
    This is the parent class for your service.

    Imagine this is you and the service you develop
    is your child.
    Your service app should do what it wants and leave
    all other obligatory tasks to its parents.

    Usage:
    .. code-block:: python

        def run():
            service = Service('/path/to/config-file.yaml')
            service.run()

        if __name__ == '__main__':
            run()

    """

    def __init__(self, conf_path, **kwargs):
        self.conf = load_yaml_conf(conf_path)
        print(f"Service.__init__:")
        print(f"\tconf: {self.conf}")
        super().__init__(
            client_max_size=self.conf.pop(
                'client_max_size', 1024 ** 2
                ),
            logger=self.conf.pop('logger', logger),
            loop=BLoop(debug=self.conf['log_level']),
            middlewares=(self.error_middleware,))
        self._services = {name: service['class'](service['config']) for
                          name, service in self.conf['services']}
        self._handler = self.conf.pop('handler', None)
        self._server = None
        self._tasks = None
        self._is_running = asyncio.Event()
        self.channels = {}
        self.websockets = {}
        print(f"server: self {vars(self)}")

        if len(self.conf['core']):
            self.loop.run_until_complete(self.setup(self.conf['core']))
        if len(self.conf['components']):
            self.loop.run_until_complete(self.setup(self.conf['components']))

        # init template render engine
        aiohttp_jinja2.setup(
            self,
            loader=jinja2.FileSystemLoader(TEMPLATES_DIR)
            )

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def is_running(self):
        """
        :return: True if self._is_running is set, False otherwise.
        :rtype: boolean
        """
        return self._is_running.is_set()

    def install(self, components):
        self._loop.run_until_complete(self.setup(components))

    async def setup(self, components):
        """
        As components should not have initial dependencies to each other
        they can be setup in parallel.
        """
        print(f"server setup:")
        print(f"\tcomponents: {components}")
        await asyncio.gather(*(
            component(self) for component in components
            ))

    async def create_channel(self, name: str):
        """create and register channels"""
        self.channels[name] = Channel()
        return self.channels[name]

    async def register_signals(self,
                               signals: (str,)
                               ):
        """
        Register signals send by a component.
        """
        for name in signals:
            self.__setattr__(name, Signal(self))
            print(f'registered signal: {name}, {self.__getattribute__(name)}')

    async def shutdown(self):
        logger.info(
            f"\n\n{'*'*10} Shutting down {HOST}:{PORT} "
            f"at {arrow.now()} {'*'*10}\n"
            )
        self._is_running.clear()

        await asyncio.gather(*(task.join() for task in self._tasks))
        self.channels.clear()
        await asyncio.gather(*(
            component.shutdown(self) for component in self._components
            ))
        await asyncio.gather(*(
            component.shutdown(self) for component in self._core
            ))
        self._server.close()
        await self._server.wait_closed()
        await self._handler.shutdown(60)

    @staticmethod
    async def error_middleware(service, handler):

        async def er_mw_handler(request):
            try:
                print(f"\n\n{__file__}{__name__}:"
                      f"\n\tGot request:"
                      f"\n\t{__name__}:"
                      f"\n\t\t{vars(service)}"
                      f"\n\thandler:"
                      f"\n\t\t{handler.__name__}.\n\n")
                return await handler(request)

            except HTTPNotFound:

                return HTTPFound('/')
            except RequestDenied as rd:

                print(
                    traceback.format_exc(rd)
                    )
                traceback.print_stack(limit=100)

                return web.json_response(
                    dict(error=f"{type(rd).__name__}: {rd}"),
                    status=401
                    )

            except Exception as e:

                print(
                    traceback.format_exc(e)
                    )
                traceback.print_stack(limit=100)

                return web.json_response(
                    dict(error=f"{type(e).__name__}: {e}"),
                    status=400
                    )

        return er_mw_handler

    async def run_channels(self):
        await self._is_running.wait()
        await asyncio.gather(*(channel.open() for channel in self.channels))

    def run(self):
        if self._handler is None:
            self._handler = self.make_handler(
                debug=DEBUG,
                secure_proxy_ssl_header=('X-Forwarded-Proto', 'https')
                )

        if not self.frozen:
            self.freeze()

        self._server = self._loop.run_until_complete(
            self._loop.create_server(
                self._handler,
                host=HOST, port=PORT
                )
            )
        self._is_running.set()
        logger.info(f"service starting {arrow.now()}")
        if DEBUG:
            for key, value in vars(self).items():
                print(f"service {key}: {value}")

        try:
            self.loop.run_until_complete(self.startup())
            self.loop.run_forever()

        except (KeyboardInterrupt, asyncio.CancelledError) as e:
            print(f"{type(e).__name__} at {__name__}.run()")
            print(f"{arrow.now()} - shutting down {__name__}")
            self.loop.run_until_complete(self.shutdown())
        except Exception as e:
            print(f"{type(e).__name__} at {self.name}.run(): {e}")
            self._loop.run_until_complete(self.shutdown())
        self._loop.stop()
        self._loop.close()
