from bonham.settings import ASSETS_DIR, ASSETS_URL
from bonham.views import index


async def setup(app):
    """
    filling router table with 
    routes: ('route', handler, name)
    request methods are defined like
      method 'GET' using router.add_get(route, handler, name=name)
      method 'POST' using router.add_post(route, handler, name=name)
      ...
      or using router.add_route('method', 'route', handler, name=name) 
    
    :param app: app.router instance
    :type router: <class 'aiohttp.web_urldispatcher.UrlDispatcher'>
    :return: None
    """
    print("start router setup", flush=True)
    app.router.add_static(ASSETS_URL, path=ASSETS_DIR)
    app.router.add_get('/', index, name='ìndex')

    print("end router setup", flush=True)
