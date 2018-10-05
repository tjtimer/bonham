"""
auth.py
Tim "tjtimer" Jedro
01.10.2018
"""
from aiohttp import web

from bonham.security import jwt

auth = web.Application()
routes = web.RouteTableDef()


@routes.get('/')
async def index(request: web.Request)->web.Response:
    print('api index handler')
    return web.Response(body=b'api index response')

@web.middleware
async def verify_access(request, handler):
    await jwt.verify_token(request.headers.get('Access'))

async def setup(app: web.Application):
    auth.add_routes(routes)
    print('auth setup done!')

