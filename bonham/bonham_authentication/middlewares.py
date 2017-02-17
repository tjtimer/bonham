from bonham.bonham_authentication.token import Token
from bonham.bonham_user.models import User


async def auth_middleware(app, handler):
    token = Token()

    async def au_middleware_handler(request):
        auth_token = request.headers.get('AUTH-TOKEN')
        if auth_token:
            r_user = await token.verify_user(auth_token)
            request['user'] = User(**r_user)
            app.logger.debug(f'\n{request["user"]}\nrequest:\n\t{request.__dict__}')
        response = await handler(request)
        return response

    return au_middleware_handler
