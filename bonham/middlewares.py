import json

from aiohttp import web
from aiohttp.web_exceptions import HTTPFound, HTTPNotFound

__all__ = [
    "engine_middleware",
    "data_middleware",
    "error_middleware"
    ]

async def error_middleware(app, handler):
    async def er_middleware_handler(request):
        try:
            response = await handler(request)
            return response
        except HTTPNotFound:
            return HTTPFound('/', headers={'REDIRECT': request.raw_path})
        except Exception as e:
            app.logger.debug(f"request error: {type(e).__name__}"
                             f"\n\trequest:\n\t{vars(request)}"
                             f"\n\targs:\n\t{[arg for arg in e.args]}\n")
            return web.json_response({
                'error': f"{type(e).__name__}: {e}"
                }, status=400)

    return er_middleware_handler


async def data_middleware(app, handler):
    async def da_middleware_handler(request):
        qs = request.rel_url.query_string
        if qs:
            request['query'] = {pair.split('=')[0]: pair.split('=')[1] for pair in qs.split('&')}
            print(f"request query: {request['query']}")
        else:
            request['query'] = {
                'offset':   0,
                'order_by': 'name',
                'limit':    50
                }
        if any(request.method in method for method in ['POST', 'PUT', 'PATCH']):
            data = await request.content.read()
            if data is not b'':
                request['data'] = json.loads(data.decode('utf-8'))
        response = await handler(request)
        return response

    return da_middleware_handler


async def db_middleware(app, handler):

    async def db_engine_handler(request):
        try:
            async with app['db'].acquire() as request['connection']:
                async with request['connection'].transaction():
                    response = await handler(request)
            return response
        except Exception as e:
            print(f"\n\ndatabase engine miwa exception:\n\t{type(e).__name__}\n\t{e}", flush=True)
            response = {
                'error': f"database error: {type(e).__name__} ->{e}"
                }
            return web.json_response(response, status=401)

    return db_engine_handler


all = [error_middleware, db_middleware, data_middleware]
