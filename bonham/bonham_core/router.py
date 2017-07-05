from collections import Coroutine

from bonham.bonham_core import views
from bonham.bonham_core.utils import kebap_case

__all__ = ['Router', 'Route', 'default_routes']


class Route(object):
    def __init__(self, method: str, path: str,
                 handler: Coroutine, name: str=None, **kwargs):
        self.method = method
        self.path = path
        self.handler = handler
        if name is None:
            name = kebap_case(self.handler.__name__)
        self.name = name
        # explicitly inject or exclude middlewares
        self.whitelist_mw = set(kwargs.pop('whitelist_mw', []))
        self.blacklist_mw = set(kwargs.pop('blacklist_mw', []))


class Router(object):

    def __init__(self):
        pass


default_routes = [
    Route('GET', '/', views.index, 'index'),
    Route('GET', '/ping/', views.ping, 'index')
    ]

