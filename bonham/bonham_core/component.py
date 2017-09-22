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

__all__ = ()

logger = logging.getLogger(__name__)


# start here
class Component:
    """
    Abstract base class for a service component,
    e.g. Authorisation/Authentication, Router, Database...
    """
    _server_components = []

    def __init_subclass__(cls, **kwargs):
        cls._server_components.append(cls)

    def __init__(self):
        self._loop = asyncio.get_event_loop()
        self._ready = asyncio.Event()

    @abstractmethod
    async def setup(self, parent):
        """setup component and attach to parent."""
        raise NotImplementedError(
            f"Child class of Component must implement a setup method!"
            )

    @abstractmethod
    async def shutdown(self, parent):
        """shutdown component"""
        pass
