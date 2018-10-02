"""
auth.py
Tim "tjtimer" Jedro
01.10.2018
"""
from aiohttp import web

auth = web.Application()
routes = web.RouteTableDef()


@routes.get('/')
async def index(request: web.Request)->web.Response:
    print('api index handler')
    return web.Response(body=b'api index response')

auth.add_routes(routes)
