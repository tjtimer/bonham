from aiohttp import web

from bonham.views import index


async def setup(app) -> web.Application:
    """
    filling router table with 
    routes: ('route', handler, name)
    request methods are defined like
      method 'GET' using router.add_get(route, handler, name=name)
      method 'POST' using router.add_post(route, handler, name=name)
      ...
      or using router.add_route('method', 'route', handler, name=name) 
    
    :param app: app.router instance
    :return: None
    """
    app.router.add_get('/', index, name='ìndex')
    return app
