from aiohttp import web

from .views import index, ping, swagger_api

__all__ = ['setup', 'shutdown']


async def shutdown(service):
    pass


async def setup(service) -> web.Application:
    """
    filling router table with
    routes: (path, handler, name)
    request methods are defined like
      method 'GET' using router.add_get(route, handler, name=name)
      method 'POST' using router.add_post(route, handler, name=name)
      ...
      or using router.add_route('method', 'route', handler, name=name)

    :param service: service.router instance
    :return: service
    """
    service.router.add_get('/', index, name='ìndex')
    service.router.add_get('/ping/', ping, name='ping')
    print(f"router setup finished:\n\tservice: {vars(service)}\n\trouter: {vars(service.router)}")
    service.router.add_get('/swagger-api/', swagger_api, name='swagger-api')
    return service
