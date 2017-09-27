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
from functools import wraps

from bonham.bonham_core.helper import snake_case

__all__ = ()

logger = logging.getLogger(__name__)


def wrap_setup(setup):
    @wraps(setup)
    async def wrapper(instance, service, *args, **kwargs):
        await setup(instance, service, *args, **kwargs)
        setattr(service, snake_case(instance.__class__.__qualname__), instance)

    return wrapper


class ComponentMeta(type):
    r""""""

    def __new__(cls, name, bases, namespace, **kwargs):
        r"""set component as attribute on service"""
        namespace['setup'] = wrap_setup(namespace['setup'])
        comp = type.__new__(cls, name, bases, dict(namespace))
        return comp


class Component(metaclass=ComponentMeta):
    """
    Abstract base class for a service component,
    e.g. Authorisation/Authentication, Contact, Blog...
    """
    __slots__ = ('_ready', '_loop')

    def __init__(self):
        self._loop = asyncio.get_event_loop()
        self._ready = asyncio.Event()

    @abstractmethod
    async def setup(self, service):
        r"""setup your component"""

    @abstractmethod
    async def shutdown(self, service):
        """shutdown component"""
        pass
