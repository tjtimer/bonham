from bonham.bonham_auth.models import Client
from bonham.bonham_auth.token import decode_token
from bonham.bonham_core import views

__all__ = ('check_bearer', 'request_signal')


async def request_signal(handler):
    async def middleware_handler(request):
        await request.app.on_auth_request_started.send(request, handler)
        return await handler(request)
        await service.on_auth_response_sent.send(request, handler)
    return middleware_handler


async def check_bearer(handler):
    async def cb(request):
        # print("bearer_middleware", flush=True)
        # print(vars(request), flush=True)
        cookie_bearer = request.cookies.get('bearer', None)
        # print(request.raw_path, cookie_bearer)
        if cookie_bearer and len(cookie_bearer.split('.')) is 3:
            async with request.app.db.acquire() as connection:
                ref_token = await Client().get_by_key(connection, key='token',
                                                      value=cookie_bearer)
            # print(f"ref_token: {ref_token}")
            if ref_token is not None:
                ref_data = await decode_token(
                    ref_token['token'].encode('utf-8'))
                # print(ref_data)  # TODO: refresh token flow!!!
            response = await views.index(request)
            if not response.prepared:
                response.headers.update({
                    'access': 'access',
                    'refresh': 'refresh'
                    })
            # print(vars(response))
            return response
        return await handler(request)

    return cb
