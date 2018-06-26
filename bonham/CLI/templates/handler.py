"""
handler
"""
from aiohttp import web

from bonham.core.app import routes


@routes.get('/handler_name', name='handler_name')
async def handler_name(request):
    """
    handler_name takes a request
    and returns a json response.
    :param request:
    :return: json
    """
    return web.json_response({'key': 'value'}, status=200)
