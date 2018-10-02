from pprint import pprint

from aiohttp import web

api = web.Application()
routes = web.RouteTableDef()


@routes.get('/')
async def index(request: web.Request)->web.Response:
    print('api index handler')
    return web.Response(body=b'api index response')

api.add_routes(routes)
