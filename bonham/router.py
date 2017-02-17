from bonham.bonham_api.v1 import app as json_api
from bonham.settings import ASSETS_DIR, ASSETS_URL
from bonham.views import index


def setup(router):
    """
    filling router table with 
    routes: ('route', handler, name)
    and sub_apps: ('route prefix', sub_app)
    request methods are defined like
      method 'GET' using router.add_get(route, handler, name=name)
      method 'POST' using router.add_post(route, handler, name=name)
      ...
      or using router.add_route('method', 'route', handler, name=name) 
    
    :param router: app.router instance
    :type router: <class 'aiohttp.web_urldispatcher.UrlDispatcher'>
    :return: None
    """
    router.add_static(ASSETS_URL, path=ASSETS_DIR)
    router.add_get('/', index, name='ìndex')
    router.add_subapp('/api/v1/', json_api)
