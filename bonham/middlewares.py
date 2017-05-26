import json

from aiohttp import web
from aiohttp.web_exceptions import HTTPFound, HTTPNotFound

from bonham.serializer import serialize

__all__ = [
    'data_middleware',
    'db_middleware',
    'error_middleware',
    'query_string_middleware',
    'serializer_middleware'
    ]

async def error_middleware(app, handler):

    async def er_mw_handler(request):
        try:
            print()
            response = await handler(request)
            print(f"returning response from error_middle_ware")
            return response
        except HTTPNotFound:
            return HTTPFound('/', headers={'REDIRECT': request.raw_path})
        except BaseException as e:
            app.logger.debug(f"request error:\n\t{type(e).__name__}\n\t{e}")
            return web.json_response({
                'error': f"{type(e).__name__}: {e}"
                }, status=400)

    return er_mw_handler

async def serializer_middleware(_, handler):

    async def se_mw_handler(request):
        if request.path in ['/']:
            response = await handler(request)
            return response
        raw_response = await handler(request)
        if isinstance(raw_response, web.Response):
            return raw_response
        if isinstance(raw_response, tuple):
            response = await serialize(request.match_info.route.resource.name, raw_response[0])
            return web.json_response(response, headers=raw_response[1], status=200)
        response = await serialize(request.match_info.route.resource.name, raw_response)
        return web.json_response(response, status=200)

    return se_mw_handler

async def query_string_middleware(_, handler):

    async def qs_mw_handler(request):
        qs = request.rel_url.query_string
        if qs:
            request['query'] = {pair.split('=')[0]: pair.split('=')[1] for pair in qs.split('&')}
            print(f"request query: {request['query']}", flush=True)
        else:
            request['query'] = {
                'offset':   0,
                'order_by': 'name',
                'limit':    50
                }
        return await handler(request)

    return qs_mw_handler

async def data_middleware(_, handler):

    async def da_mw_handler(request):
        if request.method in ['POST', 'PUT', 'PATCH']:
            data = await request.content.read()
            if data is not b'':
                request['data'] = json.loads(data.decode('utf-8'))
        return await handler(request)

    return da_mw_handler


async def db_middleware(app, handler):

    async def db_engine_handler(request):
        async with app['db'].acquire() as request['connection']:
            async with request['connection'].transaction():
                return await handler(request)

    return db_engine_handler

