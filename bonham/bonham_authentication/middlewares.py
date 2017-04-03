from aiohttp import web
import jwt

from bonham.bonham_authentication.models import Account
from .token import verify_token


async def auth_middleware(app, handler):
    async def au_middleware_handler(request):
        request['auth_token'] = request.headers.get('AUTH-TOKEN')
        request['is_authenticated'] = False
        if request['auth_token']:
            try:
                r_user = await verify_token(request=request)
                request['account'] = await db.get_by_id(
                        request['connection'], table=Account.__table__,
                        object_id=r_user['id'])
                if request['account']['disabled']:
                    return web.json_response(dict(error=f"Your account was disabled."), status=403)
                request['is_authenticated'] = True
                response = await handler(request)
                return response
            except jwt.ExpiredSignatureError as e:
                response = dict(error=f"Your authentication token has expired.")
                status = 401
                data = {'logged_in': False, 'id': e}
                await db.update(connection=request['connection'], table=Account.__table__, data=data)
                if "logout" in request.raw_path:
                    response = dict(message=f"{request['account'].email} successfully logged out.")
                    status = 200
                return web.json_response(response, status=status)
            except jwt.DecodeError as e:
                return web.json_response(dict(error=f"{e}"), status=400)
        response = await handler(request)
        return response

    return au_middleware_handler
