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
        except HTTPNotFound as e:
            print(f"HTTPNotFound: {e}\nrequest.raw_path: {request.raw_path}", flush=True)
            return HTTPFound('/', headers={ 'REDIRECT': request.raw_path })
        except Exception as e:
            app.logger.debug(f"request error: {type(e).__name__}"
                             f"\n\trequest:\n\t{vars(request)}"
                             f"\n\targs:\n\t{[arg for arg in e.args]}\n")
            return web.json_response({
                'message': {
                    'type': 'error',
                    'message': f"{type(e).__name__}: {e}"
                    }
                }, status=400)

    return er_middleware_handler


async def data_middleware(app, handler):
    async def da_middleware_handler(request):
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
            print(f"\n\ndb engine middleware exception:\n\t{type(e).__name__}\n\t{e}", flush=True)
            response = {
                'message': {
                    'type'   : 'error',
                    'message': f"database error: {type(e).__name__} ->{e}"
                    }
                }
            return response

    return db_engine_handler


all = [error_middleware, db_middleware, data_middleware]
