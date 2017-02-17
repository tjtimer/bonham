import json

from aiohttp import web
from aiohttp.web_exceptions import HTTPFound, HTTPNotFound


async def error_middleware(app, handler):
    async def er_middleware_handler(request):
        try:
            response = await handler(request)
            return response
        except HTTPNotFound as e:
            print(f"HTTPNotFound: {e}\nrequest.raw_path: {request.raw_path}")
            return HTTPFound('/', headers={ 'REDIRECT': request.raw_path })
        except Exception as e:
            app.logger.debug('\trequest error: {}\n\trequest:\n\t{}\n\targs:\n\t{}\n'.format(
                    type(e).__name__,
                    request.__dict__,
                    [arg for arg in e.args]))
            return web.json_response({ 'message': { 'type': 'error', 'message': e.__str__() } }, status=400)

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


async def engine_middleware(app, handler):
    async def db_engine_handler(request):
        if 'assets' in request.path:
            response = await handler(request)
            return response
        try:
            async with app['db'].acquire() as request['connection']:
                response = await handler(request)
            return response
        except Exception as e:
            print('\n\nengine middleware exception:\n\t{}\n\t{}'.format(type(e).__name__, e), flush=True)
            response = {
                'message': {
                    'type': 'error',
                    'message': 'database error: {} ->{}'.format(type(e).__name__, e)
                }
            }
            return response

    return db_engine_handler
