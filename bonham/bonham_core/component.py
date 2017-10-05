"""
Name: bonham - component 
Author: Tim "tjtimer" Jedro
Email: tjtimer@gmail.com
Version: 0.0.1dev

created: 21.09.17 09:59
"""
import asyncio
import logging
from abc import abstractmethod

from aiohttp import web

__all__ = ()

logger = logging.getLogger(__name__)

available_components = {}


class Component(web.Application):
    """
    Abstract base class for a service component,
    e.g. Authorisation/Authentication, Contact, Blog...
    """

    __slots__ = ()

    def __init_subclass__(cls, **kwargs):
        print(f"Component.__init_subclass__")
        print(f"cls: {cls}")
        print(f"kwargs")
        available_components[cls.__name__] = cls

    def __init__(self, **kwargs):
        print(f"Component.__init__")
        print(f"self: {self}")
        print(f"service: {service}")
        super().__init__(**kwargs)
        self.handler = None
        self.ready = asyncio.Event()
        self.loop.run_until_complete(self.setup())

    @abstractmethod
    async def setup(self):
        r"""setup your component"""

    @abstractmethod
    async def shutdown(self):
        """shutdown component"""
        pass
