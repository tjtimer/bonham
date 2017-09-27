from collections import Generator, Iterator
from typing import NamedTuple

from aiohttp.web_urldispatcher import UrlDispatcher

from bonham.bonham_core.component import Component
from bonham.bonham_core.views import index, ping

__all__ = ['Route', 'Router']

Route = NamedTuple('Route', method=str, path=str, handler=callable, name=str)


class Router(Component, UrlDispatcher):
    r"""Router"""

    def __init__(self):
        super().__init__()

    async def setup(self, service):
        """
        filling router table with
        ROUTES: (path, handler, name)
        request methods are defined like
          method 'GET' using router.add_get(route, handler, name=name)
          method 'POST' using router.add_post(route, handler, name=name)
          ...
          or using router.add_route('method', 'route', handler, name=name)

        :param service: service instance
        :return: service: service instance
        """
        self.add_get('/', index, name='index')
        self.add_get('/ping/', ping, name='ping')
        service._router = self

    async def shutdown(self, parent):
        """shutdown component"""
        pass

    async def register(self, routes: (Generator, Iterator), prefix='/'):
        """
        Register ROUTES.

        Usage:
            '''python
            class MyComponent(Component):
                async def setup(self, service):
                    await service.router.register(my_routes)
                    ...
            '''
            where my_routes is any iterable that returns
            a collection of ROUTES.

            A route is a namedtuple ('method', 'path', 'handler', 'name').

        """
        for route in routes:
            self.add_route(route.method, f"{prefix}{route.path}",
                           route.handler, name=route.name)
