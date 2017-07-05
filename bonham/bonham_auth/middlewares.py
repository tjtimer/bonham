import jwt
from aiohttp import web

from bonham.bonham_auth.models import RefreshToken
from bonham.bonham_core import views
from .token import decode_token, verify_token

__all__ = ['access_middleware']


async def request_signal_middleware(service, handler):
    async def middleware_handler(request):
        await service.on_auth_request_started.send(request, handler)
        return await handler(request)
        await service.on_auth_response_sent.send(request, handler)
    return middleware_handler


async def bearer_middleware(_, handler):
    async def br_mw_handler(request):
        print("bearer_middleware", flush=True)
        print(vars(request), flush=True)
        cookie_bearer = request.cookies.get('bearer', None)
        print(request.raw_path, cookie_bearer)
        if cookie_bearer:
            ref_token = await RefreshToken().get_by_key(request['connection'], key='token', value=cookie_bearer)
            ref_data = await decode_token(ref_token['token'].encode('utf-8'))
            print(ref_data)  # TODO: refresh token flow!!!
            response = await views.index(request)
            if not response.prepared:
                response.headers.update({
                    'access': 'access',
                    'refresh': 'refresh'
                    })
            print(vars(response))
            return response

    return br_mw_handler


async def access_middleware(app, handler):
    async def au_middleware_handler(request):
        print("access_middleware", flush=True)
        print(vars(request), flush=True)
        request['auth_token'] = request.headers.get('access', None)
        if request['auth_token']:

            try:
                request['account'] = await verify_token(token=request['auth_token'])
                request['is_authenticated'] = True
                return await handler(request)

            except jwt.ExpiredSignatureError as e:
                if "logout" in request.raw_path:
                    return await handler(request)

                return web.json_response(dict(error=f"{e}"), status=401)

            except jwt.DecodeError as e:
                return web.json_response(dict(error=f"{e}"), status=400)
        request['is_authenticated'] = False
        return await handler(request)

    return au_middleware_handler
