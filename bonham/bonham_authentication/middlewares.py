import jwt
from aiohttp import web

from bonham.bonham_authentication.models import Account
from bonham.bonham_authentication.token import Token


async def auth_middleware(app, handler):
    print(f"app: {vars(app)}\nhandler: {handler.__name__}", flush=True)
    async def au_middleware_handler(request):
        auth_token = request.headers.get('AUTH-TOKEN')
        request['account'] = Account()
        if auth_token:
            try:
                r_user = await Token(loop=app.loop).verify_token(token=auth_token)
                vars(request['account']).update(**r_user)
                response = await handler(request)
                return response
            except (jwt.DecodeError, jwt.ExpiredSignatureError) as e:
                return web.json_response({
                    'message': {
                        'type'   : 'error',
                        "message": f"Token invalid! {type(e).__name__} -> {e}"
                        }
                    }, status=400)
            finally:
                app.logger.debug(f"\nrequest:\n\t{vars(request)}")
        response = await handler(request)
        return response

    return au_middleware_handler
