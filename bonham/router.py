from bonham.bonham_api.v1 import init_api
from bonham.views import index


async def setup(app):
    """
    filling router table with 
    routes: ('route', handler, name)
    and sub_apps: ('route prefix', sub_app)
    request methods are defined like
      method 'GET' using router.add_get(route, handler, name=name)
      method 'POST' using router.add_post(route, handler, name=name)
      ...
      or using router.add_route('method', 'route', handler, name=name) 
    
    :param app: app.router instance
    :type router: <class 'aiohttp.web_urldispatcher.UrlDispatcher'>
    :return: None
    """
    app.add_subapp('/api/v1', await init_api(loop=app.loop))
    # app.router.add_static(ASSETS_URL, path=ASSETS_DIR)
    app.router.add_get('/', index, name='ìndex')
